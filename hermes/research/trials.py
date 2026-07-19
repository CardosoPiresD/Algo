"""Registre d'essais append-only — QW-8 (docs/HERMES_V2_ROADMAP.md).

L'honnêteté du n_trials devient mécanique, plus déclarative : chaque run de
backtest est enregistré automatiquement par le harnais avec le hash de sa
config et le hash de ses données. Le Deflated Sharpe Ratio lit ce registre —
n_trials = TOTAL des essais comptés, jamais un sous-ensemble par « famille »
(porte dérobée supprimée par le critique).

Règle de comptage pré-enregistrée :
- même config + mêmes données  -> non recompté (même clé)
- même config + données rafraîchies -> compté une fois par millésime de données
- config nouvelle -> essai plein
Un run sans champ `hypothese` est marqué `exploratoire` : compté dans n_trials
(il consomme un degré de liberté) mais jamais promouvable en production.
"""

import hashlib
import json
import os
from datetime import datetime, timezone

import numpy as np

# Degrés de liberté historiques déjà consommés avant la mise en place du
# registre (design v2 §5 couche 7) — jamais remis à zéro.
HISTORICAL_TRIALS_BASELINE = 10


def config_hash(config: dict) -> str:
    canonical = json.dumps(config, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def data_hash(prices) -> str:
    """Hash du contenu des données d'entrée (millésime yfinance inclus)."""
    h = hashlib.sha256()
    h.update(str(list(prices.columns)).encode())
    h.update(str(prices.index[0]).encode())
    h.update(str(prices.index[-1]).encode())
    h.update(np.ascontiguousarray(prices.to_numpy(dtype=float)).tobytes())
    return h.hexdigest()[:16]


class TrialsRegistry:
    def __init__(self, path: str = "hermes/research/trials_registry.jsonl"):
        self.path = path

    def _load(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        entries = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def record(
        self,
        config: dict,
        metrics: dict,
        data_h: str,
        hypothese: str | None = None,
        git_commit: str | None = None,
    ) -> dict:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "config_hash": config_hash(config),
            "data_hash": data_h,
            "config": config,
            "metrics": metrics,
            "hypothese": hypothese,
            "statut": "hypothese" if hypothese else "exploratoire",
            "git_commit": git_commit,
        }
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        return entry

    def n_trials(self) -> int:
        """Nombre d'essais distincts (clé config+données) + base historique."""
        seen = {(e["config_hash"], e["data_hash"]) for e in self._load()}
        return HISTORICAL_TRIALS_BASELINE + len(seen)

    def sharpe_variance(self) -> float | None:
        """Variance empirique des Sharpes enregistrés (>= 3 essais distincts).

        Injectée dans le DSR conformément à Bailey & López de Prado, au lieu
        de l'approximation sous H0 seule.
        """
        by_key: dict[tuple, float] = {}
        for e in self._load():
            sr = e.get("metrics", {}).get("sharpe")
            if sr is not None:
                by_key[(e["config_hash"], e["data_hash"])] = float(sr)
        if len(by_key) < 3:
            return None
        return float(np.var(list(by_key.values()), ddof=1))
