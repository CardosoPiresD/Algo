"""Enveloppe statistique par block bootstrap — QW-6 (docs/HERMES_V2_ROADMAP.md).

Rend mécaniques les seuils de surveillance 🟢/🟠/🔴 du paper trading : le
backtest validé est rééchantillonné par blocs (préservant l'autocorrélation),
APRÈS application du haircut McLean-Pontiff de −58 % pré-enregistré (la
décroissance post-publication documentée — rapport §2.1). Bootstrapper le
backtest brut placerait la barre là où le paper est PRÉVU de la rater.

Sortie : percentiles pré-enregistrés de Sharpe glissant 12 mois, max drawdown
et ES 97,5 %, à écrire dans state/backtest_envelope.json versionné au tag git.
Taux de fausses alertes assumé : sous le percentile 20 ≈ un trimestre 🟠 sur
cinq même si tout va bien.

C'est de la MESURE, pas du signal — zéro paramètre côté stratégie.
"""

import json

import numpy as np
import pandas as pd

from hermes.reporting.tearsheet import expected_shortfall

MCLEAN_PONTIFF_HAIRCUT = 0.58
TRADING_DAYS_PER_YEAR = 252


def apply_haircut(returns: pd.Series, haircut: float = MCLEAN_PONTIFF_HAIRCUT) -> pd.Series:
    """Dégrade l'espérance des rendements de `haircut` sans toucher la vol.

    r'_t = r_t − haircut × mean(r) : la moyenne devient (1−haircut)×mean,
    l'écart-type est inchangé.
    """
    r = returns.dropna()
    return r - haircut * r.mean()


def _block_bootstrap_indices(n: int, block_len: int, rng: np.random.Generator) -> np.ndarray:
    starts = rng.integers(0, max(1, n - block_len + 1), size=(n // block_len) + 1)
    idx = np.concatenate([np.arange(s, s + block_len) for s in starts])
    return idx[:n]


def bootstrap_envelope(
    returns: pd.Series,
    block_len: int = 63,
    n_boot: int = 2000,
    haircut: float = MCLEAN_PONTIFF_HAIRCUT,
    seed: int = 42,
    percentiles: tuple = (5, 20, 50, 80, 95),
) -> dict:
    """Percentiles bootstrap de Sharpe 12 mois glissant, max DD et ES 97,5 %."""
    base = apply_haircut(returns, haircut).to_numpy()
    n = len(base)
    if n < block_len * 2:
        raise ValueError(f"Historique insuffisant: {n} < {block_len * 2}")
    rng = np.random.default_rng(seed)
    window = TRADING_DAYS_PER_YEAR

    sharpes, maxdds, ess = [], [], []
    for _ in range(n_boot):
        sample = base[_block_bootstrap_indices(n, block_len, rng)]
        s = pd.Series(sample)
        # Sharpe glissant 12 mois : le pire des Sharpes glissants du chemin
        # (c'est lui qu'on comparera au Sharpe glissant du paper).
        if n > window:
            roll_mean = s.rolling(window).mean().dropna()
            roll_std = s.rolling(window).std().dropna()
            roll_sharpe = (roll_mean / roll_std.replace(0, np.nan)).dropna() * np.sqrt(
                TRADING_DAYS_PER_YEAR
            )
            sharpes.append(float(roll_sharpe.min()) if not roll_sharpe.empty else 0.0)
        else:
            mu, sd = s.mean(), s.std()
            sharpes.append(float(mu / sd * np.sqrt(TRADING_DAYS_PER_YEAR)) if sd > 0 else 0.0)
        equity = (1 + s).cumprod()
        peak = equity.cummax()
        maxdds.append(float(((peak - equity) / peak).max()))
        ess.append(expected_shortfall(s, 0.975))

    def pct(values):
        return {f"p{p}": float(np.percentile(values, p)) for p in percentiles}

    return {
        "params": {
            "block_len": block_len,
            "n_boot": n_boot,
            "haircut": haircut,
            "seed": seed,
            "n_obs": n,
        },
        "note_fausses_alertes": (
            "Sous le percentile 20 = un trimestre orange sur cinq même si tout "
            "va bien — pré-enregistré pour que le futur soi ne panique pas."
        ),
        "rolling_sharpe_12m_worst": pct(sharpes),
        "max_drawdown": pct(maxdds),
        "es_975": pct(ess),
    }


def write_envelope(envelope: dict, path: str = "state/backtest_envelope.json") -> str:
    import os

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(envelope, f, indent=1)
    return path
