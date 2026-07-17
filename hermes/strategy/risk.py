"""Gestion du risque : sizing inverse-vol, demi-Kelly, trailing stops, coupe-circuit.

Base académique (voir research/RAPPORT_BOURSE.md §7 et complément 8bis) :
- Vol-scaling conservateur (les gains du vol-timing agressif sont contestés
  hors-échantillon/après coûts — Cederburg et al. 2020, Barroso & Detzel 2021).
- Kelly fractionnaire (le Kelly plein sur données échantillonnées est mal
  calibré dans les deux sens — Hsieh, Barmish & Gubner 2016).
- Trailing stops larges plutôt que serrés (Lo & Remorov 2017 : les stops serrés
  sous-performent sur actions individuelles à cause des coûts).
"""

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


@dataclass
class RiskParams:
    vol_lookback_days: int = 60
    target_annual_vol: float = 0.15
    max_position_weight: float = 0.30
    kelly_fraction: float = 0.5
    trailing_stop_pct: float = 0.15
    max_drawdown_circuit_breaker: float = 0.15
    kill_switch_file: str = "KILL_SWITCH"


def inverse_vol_weights(prices: pd.DataFrame, selected: pd.Series, params: RiskParams) -> pd.Series:
    """Repondère les titres sélectionnés en inverse de leur volatilité réalisée."""
    if selected.empty:
        return selected
    returns = prices[selected.index].pct_change().iloc[-params.vol_lookback_days :]
    vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    vol = vol.replace(0, np.nan).dropna()
    if vol.empty:
        return selected
    inv = 1.0 / vol
    weights = inv / inv.sum()
    return weights.clip(upper=params.max_position_weight)


def portfolio_vol_scalar(
    prices: pd.DataFrame, weights: pd.Series, params: RiskParams
) -> float:
    """Facteur d'exposition global: target_vol / vol réalisée du portefeuille.

    Plafonné à 1.0 (jamais de levier) puis multiplié par la fraction de Kelly.
    """
    if weights.empty:
        return 0.0
    returns = prices[weights.index].pct_change().iloc[-params.vol_lookback_days :]
    port_returns = returns.mul(weights, axis=1).sum(axis=1)
    realized = port_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    if realized == 0 or np.isnan(realized):
        return 0.0
    scalar = min(1.0, params.target_annual_vol / realized)
    return scalar * params.kelly_fraction * 2  # demi-Kelly sur exposition max 1.0


def apply_risk_overlay(
    prices: pd.DataFrame, selected: pd.Series, params: RiskParams
) -> pd.Series:
    """Pipeline complet: inverse-vol -> vol target -> plafond par position."""
    weights = inverse_vol_weights(prices, selected, params)
    scalar = portfolio_vol_scalar(prices, weights, params)
    final = (weights * min(scalar, 1.0)).clip(upper=params.max_position_weight)
    return final


def trailing_stop_triggered(
    entry_high: float, current_price: float, params: RiskParams
) -> bool:
    """True si le prix a chuté de plus de trailing_stop_pct depuis le plus haut."""
    if entry_high <= 0:
        return False
    return (entry_high - current_price) / entry_high >= params.trailing_stop_pct


def circuit_breaker_triggered(equity_curve: pd.Series, params: RiskParams) -> bool:
    """True si le drawdown courant du portefeuille dépasse le seuil configuré."""
    if equity_curve.empty:
        return False
    peak = equity_curve.cummax()
    drawdown = (peak - equity_curve) / peak
    return bool(drawdown.iloc[-1] >= params.max_drawdown_circuit_breaker)


def kill_switch_active(params: RiskParams, root: str = ".") -> bool:
    """True si le fichier kill switch existe — aucun ordre ne doit partir."""
    return os.path.exists(os.path.join(root, params.kill_switch_file))
