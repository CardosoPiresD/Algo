"""Client LLM générique — OpenRouter (compatible OpenAI), défaut DeepSeek.

Doctrine (docs/HERMES_V2_DESIGN.md §3) : l'IA ANALYSE, ne trade jamais. Ce
client ne connaît ni le courtier, ni les tailles de positions, ni le capital.
Il renvoie du JSON structuré validé ; toute erreur (réseau, parse, refus,
budget) => None, et l'appelant dégrade en quant pur (fail-open).

Clé lue dans l'environnement (OPENROUTER_API_KEY) — JAMAIS committée. Le
modèle et l'URL viennent de la config, jamais codés en dur (design §3.4).
Implémentation stdlib (urllib) : aucune dépendance lourde à maintenir.
"""

import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-chat"
API_KEY_ENV = "OPENROUTER_API_KEY"


class LLMResult:
    def __init__(self, data: dict, prompt_tokens: int, completion_tokens: int, raw: str):
        self.data = data
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.raw = raw


class LLMClient:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        api_key_env: str = API_KEY_ENV,
        timeout: int = 60,
        max_retries: int = 2,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key_env = api_key_env
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def available(self) -> bool:
        """L'IA est-elle utilisable ? (clé présente). Sinon: quant pur."""
        return bool(os.environ.get(self.api_key_env, "").strip())

    def _post(self, payload: dict) -> dict:
        key = os.environ.get(self.api_key_env, "").strip()
        if not key:
            raise RuntimeError(f"{self.api_key_env} absente de l'environnement")
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            self.base_url,
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                # En-têtes d'attribution OpenRouter (facultatifs mais propres)
                "HTTP-Referer": "https://github.com/CardosoPiresD/Algo",
                "X-Title": "HermesBot",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.load(resp)

    def complete_json(
        self, system: str, user: str, temperature: float = 0.0
    ) -> LLMResult | None:
        """Un appel, sortie JSON. Renvoie None à la moindre anomalie (fail-open).

        Le hook `_post` est monkeypatché dans les tests — aucune connexion
        réseau n'est requise pour tester la logique.
        """
        payload = {
            "model": self.model,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        last_err = None
        for attempt in range(self.max_retries + 1):
            try:
                data = self._post(payload)
                choice = data["choices"][0]["message"]["content"]
                parsed = json.loads(choice)
                usage = data.get("usage", {})
                return LLMResult(
                    data=parsed,
                    prompt_tokens=int(usage.get("prompt_tokens", 0)),
                    completion_tokens=int(usage.get("completion_tokens", 0)),
                    raw=choice,
                )
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
                # Réponse mal formée ou JSON invalide : pas de retry utile.
                last_err = e
                break
        return None


class MeteredClient:
    """Enveloppe un LLMClient et décrémente un BudgetGuard à chaque appel.

    Coupe DUR au plafond : une fois le budget épuisé, complete_json renvoie None
    sans appeler le modèle (le cycle continue en quant pur). C'est la mise en
    œuvre concrète de la coupure budgétaire du design §3.4.
    """

    def __init__(self, client: "LLMClient", budget, month: str):
        self._client = client
        self._budget = budget
        self._month = month

    @property
    def available(self) -> bool:
        return self._client.available and self._budget.can_spend(self._month)

    def complete_json(self, system: str, user: str, temperature: float = 0.0):
        if not self._budget.can_spend(self._month):
            return None
        result = self._client.complete_json(system, user, temperature)
        if result is not None:
            self._budget.record(
                self._month, result.prompt_tokens, result.completion_tokens
            )
        return result
