"""Signal momentum : cross-sectionnel (12-1) + filtre time-series.

Base académique (voir research/RAPPORT_BOURSE.md §1.2) :
- Jegadeesh & Titman (1993, 2001) — momentum cross-sectionnel, persistance 1-12 mois.
- Moskowitz, Ooi & Pedersen (2012) — time-series momentum.
- Le mois le plus récent est exclu (skip) à cause du short-term reversal.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS_PER_MONTH = 21


@dataclass
class MomentumParams:
    lookback_months: int = 12
    skip_months: int = 1
    top_n: int = 5
    tsmom_filter: bool = True


def momentum_score(prices: pd.DataFrame, params: MomentumParams) -> pd.Series:
    """Rendement cumulé sur [t-lookback, t-skip] pour chaque colonne.

    prices: DataFrame de prix ajustés (index=date, colonnes=tickers).
    Retourne une Series (ticker -> score) datée de la dernière ligne.
    """
    lb = params.lookback_months * TRADING_DAYS_PER_MONTH
    skip = params.skip_months * TRADING_DAYS_PER_MONTH
    if len(prices) < lb + 1:
        raise ValueError(
            f"Historique insuffisant: {len(prices)} lignes < {lb + 1} requises"
        )
    past = prices.iloc[-(lb + 1)]
    recent = prices.iloc[-(skip + 1)] if skip > 0 else prices.iloc[-1]
    return recent / past - 1.0


def select_portfolio(prices: pd.DataFrame, params: MomentumParams) -> pd.Series:
    """Sélectionne les top_n titres par momentum, filtrés TSMOM si activé.

    Retourne une Series (ticker -> poids égal) ; somme < 1 possible si le
    filtre TSMOM élimine des candidats (le reste est du cash).
    """
    scores = momentum_score(prices, params).dropna()
    if params.tsmom_filter:
        scores = scores[scores > 0]
    winners = scores.nlargest(params.top_n)
    if winners.empty:
        return pd.Series(dtype=float)
    return pd.Series(1.0 / params.top_n, index=winners.index)


def momentum_scores_history(
    prices: pd.DataFrame, params: MomentumParams, rebalance_dates: pd.DatetimeIndex
) -> pd.DataFrame:
    """Scores de momentum à chaque date de rebalancing (pour le backtest)."""
    rows = {}
    for date in rebalance_dates:
        window = prices.loc[:date]
        lb = params.lookback_months * TRADING_DAYS_PER_MONTH
        if len(window) < lb + 1:
            continue
        rows[date] = momentum_score(window, params)
    return pd.DataFrame(rows).T


def rebalance_schedule(index: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    """Dernier jour de bourse de chaque période (mois ou semaine)."""
    s = pd.Series(index=index, data=index)
    period = "M" if freq == "monthly" else "W"
    return pd.DatetimeIndex(s.groupby(index.to_period(period)).last().values)
