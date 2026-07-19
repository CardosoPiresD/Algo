"""Rapports de performance : métriques clés + tearsheet HTML via QuantStats.

QW-12 (docs/HERMES_V2_ROADMAP.md) : Expected Shortfall 97,5 %, CDaR et Ulcer
Index en numpy pur — pas de CVXPY/Riskfolio dans le chemin de production
(Riskfolio-Lib ne sert que d'oracle de test en environnement de recherche).
L'ES est la mesure cohérente préférée à la VaR (Artzner et al. 1999 — rapport
complément 8bis : la VaR échoue à la sous-additivité).
"""

import os

import numpy as np
import pandas as pd


def expected_shortfall(returns: pd.Series, alpha: float = 0.975) -> float:
    """ES historique : perte moyenne au-delà du quantile (1-alpha).

    Convention : retourne une grandeur POSITIVE (une perte). ES 97,5 % =
    moyenne des pires 2,5 % de rendements, en valeur absolue.
    """
    r = returns.dropna().to_numpy()
    if len(r) == 0:
        return 0.0
    cutoff = np.quantile(r, 1 - alpha)
    tail = r[r <= cutoff]
    if len(tail) == 0:
        return 0.0
    return float(-tail.mean())


def drawdown_series(returns: pd.Series) -> pd.Series:
    equity = (1 + returns.dropna()).cumprod()
    peak = equity.cummax()
    return (peak - equity) / peak


def cdar(returns: pd.Series, alpha: float = 0.95) -> float:
    """Conditional Drawdown at Risk : moyenne des pires (1-alpha) drawdowns."""
    dd = drawdown_series(returns).to_numpy()
    if len(dd) == 0:
        return 0.0
    cutoff = np.quantile(dd, alpha)
    tail = dd[dd >= cutoff]
    if len(tail) == 0:
        return float(dd.max())
    return float(tail.mean())


def ulcer_index(returns: pd.Series) -> float:
    """Ulcer Index : racine de la moyenne des drawdowns au carré."""
    dd = drawdown_series(returns).to_numpy()
    if len(dd) == 0:
        return 0.0
    return float(np.sqrt(np.mean(dd**2)))


def summary_metrics(returns: pd.Series, periods_per_year: int = 252) -> dict:
    r = returns.dropna()
    if r.empty:
        return {}
    equity = (1 + r).cumprod()
    dd = drawdown_series(r)
    ann_ret = (1 + r.mean()) ** periods_per_year - 1
    ann_vol = r.std() * np.sqrt(periods_per_year)
    return {
        "total_return": float(equity.iloc[-1] - 1),
        "annual_return": float(ann_ret),
        "annual_vol": float(ann_vol),
        "sharpe": float(ann_ret / ann_vol) if ann_vol > 0 else 0.0,
        "max_drawdown": float(dd.max()),
        "es_975": expected_shortfall(r, 0.975),
        "cdar_95": cdar(r, 0.95),
        "ulcer_index": ulcer_index(r),
        "win_rate": float((r > 0).mean()),
        "n_periods": len(r),
    }


def html_tearsheet(
    returns: pd.Series,
    benchmark: pd.Series | None = None,
    output_dir: str = "reports",
    name: str = "hermes",
) -> str:
    """Génère un tearsheet HTML complet via QuantStats. Retourne le chemin."""
    import quantstats as qs

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}_tearsheet.html")
    qs.reports.html(returns, benchmark=benchmark, output=path, title=f"Hermes — {name}")
    return path
