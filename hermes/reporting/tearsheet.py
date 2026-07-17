"""Rapports de performance : métriques clés + tearsheet HTML via QuantStats."""

import os

import numpy as np
import pandas as pd


def summary_metrics(returns: pd.Series, periods_per_year: int = 252) -> dict:
    r = returns.dropna()
    if r.empty:
        return {}
    equity = (1 + r).cumprod()
    peak = equity.cummax()
    drawdown = (peak - equity) / peak
    ann_ret = (1 + r.mean()) ** periods_per_year - 1
    ann_vol = r.std() * np.sqrt(periods_per_year)
    return {
        "total_return": float(equity.iloc[-1] - 1),
        "annual_return": float(ann_ret),
        "annual_vol": float(ann_vol),
        "sharpe": float(ann_ret / ann_vol) if ann_vol > 0 else 0.0,
        "max_drawdown": float(drawdown.max()),
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
