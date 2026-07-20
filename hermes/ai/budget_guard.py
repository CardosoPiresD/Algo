"""Garde-fou de budget IA — design v2 §3.4.

Compteur persistant alimenté par l'usage réel (tokens) et un barème de prix
configurable (jamais codé en dur : les tarifs changent). Coupure DURE au
plafond mensuel => l'IA est désactivée pour le reste du mois, le bot continue
en quant pur. Doublé, côté opérateur, d'un spend limit configuré directement
dans la console du fournisseur (le vrai garde-fou dur).

Le mois est identifié par 'YYYY-MM' fourni par l'appelant (le code de trading
n'appelle jamais Date.now() implicitement — la date vient du cycle).
"""

import json
import os
import tempfile


class BudgetGuard:
    def __init__(
        self,
        monthly_cap_eur: float,
        price_in_per_mtok: float,
        price_out_per_mtok: float,
        path: str = "state/api_spend.json",
    ):
        self.cap = monthly_cap_eur
        self.price_in = price_in_per_mtok
        self.price_out = price_out_per_mtok
        self.path = path

    def _load(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        return {}

    def _save(self, data: dict) -> None:
        directory = os.path.dirname(self.path) or "."
        os.makedirs(directory, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, self.path)

    def spent(self, month: str) -> float:
        return float(self._load().get(month, 0.0))

    def remaining(self, month: str) -> float:
        return max(0.0, self.cap - self.spent(month))

    def can_spend(self, month: str) -> bool:
        return self.remaining(month) > 0.0

    def cost_of(self, prompt_tokens: int, completion_tokens: int) -> float:
        return (
            prompt_tokens / 1_000_000 * self.price_in
            + completion_tokens / 1_000_000 * self.price_out
        )

    def record(self, month: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Ajoute le coût d'un appel et renvoie le total du mois."""
        cost = self.cost_of(prompt_tokens, completion_tokens)
        data = self._load()
        data[month] = round(float(data.get(month, 0.0)) + cost, 6)
        self._save(data)
        return data[month]
