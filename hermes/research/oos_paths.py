"""Chemins hors-échantillon combinatoires avec embargo court — QW-10d.

Au lieu d'un Sharpe unique sur toute la période (un point), on génère une
DISTRIBUTION de Sharpes hors-échantillon : la série de rendements est découpée
en N blocs ; chaque combinaison de N/2 blocs forme un chemin d'évaluation, avec
un EMBARGO de quelques jours retiré aux jonctions de blocs (l'autocorrélation
de part et d'autre d'une coupure fuit sinon d'un chemin à l'autre).

Calibration corrigée par le critique (roadmap QW-10d) : embargo 1-2 MOIS
maximum, PAS de purge de 12 mois — les rendements de stratégie réalisés ne
fuient pas comme des labels ML ; purger 12 mois sur ~180 observations viderait
le test. (Gap explicite du corpus cycle 3 §3.5/3.6.)
"""

from itertools import combinations

import numpy as np
import pandas as pd

from hermes.backtest.validate import sharpe_ratio


def oos_path_distribution(
    returns: pd.Series,
    n_blocks: int = 8,
    embargo_days: int = 21,
    max_paths: int = 70,
    risk_free_annual=0.0,
) -> dict:
    """Distribution de Sharpes sur les chemins combinatoires OOS."""
    r = returns.dropna()
    if len(r) < n_blocks * 2 * embargo_days:
        raise ValueError(
            f"Historique insuffisant: {len(r)} obs pour {n_blocks} blocs "
            f"avec embargo {embargo_days} j"
        )
    blocks = np.array_split(np.arange(len(r)), n_blocks)
    half = n_blocks // 2

    combos = list(combinations(range(n_blocks), half))
    if len(combos) > max_paths:
        # Sous-échantillonnage déterministe régulier des combinaisons
        step = len(combos) / max_paths
        combos = [combos[int(i * step)] for i in range(max_paths)]

    sharpes = []
    for combo in combos:
        idx_parts = []
        for b in combo:
            block = blocks[b]
            # Embargo aux jonctions : on retire embargo_days au début du bloc
            # s'il ne suit pas immédiatement le bloc précédent du même chemin.
            start = embargo_days if (b - 1) not in combo else 0
            trimmed = block[start:]
            if len(trimmed):
                idx_parts.append(trimmed)
        if not idx_parts:
            continue
        path = r.iloc[np.concatenate(idx_parts)]
        sharpes.append(sharpe_ratio(path, risk_free_annual=risk_free_annual))

    values = np.array(sharpes)
    return {
        "n_paths": len(values),
        "n_blocks": n_blocks,
        "embargo_days": embargo_days,
        "sharpe_mean": float(values.mean()),
        "sharpe_p5": float(np.percentile(values, 5)),
        "sharpe_p50": float(np.percentile(values, 50)),
        "sharpe_p95": float(np.percentile(values, 95)),
        "share_negative": float((values < 0).mean()),
    }
