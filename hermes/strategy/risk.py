"""Gestion du risque : sizing inverse-vol + vol-target, trailing stops, coupe-circuit.

Base académique (voir research/RAPPORT_BOURSE.md §7 et complément 8bis) :
- Vol-scaling conservateur (les gains du vol-timing agressif sont contestés
  hors-échantillon/après coûts — Cederburg et al. 2020, Barroso & Detzel 2021).
- Trailing stops larges plutôt que serrés (Lo & Remorov 2017 : les stops serrés
  sous-performent sur actions individuelles à cause des coûts).

Note d'honnêteté (correction v2, cf. docs/HERMES_V2_DESIGN.md §2.2) : le sizing
conservateur de ce module EST la combinaison vol-target 15 % + zéro levier +
plafonds par position. Aucun critère de Kelly n'est estimé ici — la version v1
prétendait appliquer un « demi-Kelly » via un facteur ×0,5×2 qui était un no-op
arithmétique ; il a été supprimé plutôt que maquillé.
"""

import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


@dataclass
class RiskParams:
    vol_lookback_days: int = 60
    target_annual_vol: float = 0.15
    max_position_weight: float = 0.15
    trailing_stop_pct: float = 0.15
    max_drawdown_circuit_breaker: float = 0.15
    # Ré-entrée pré-enregistrée après coupe-circuit (design v2 §5 couche 3) :
    # reprise au premier rebalancement où le drawdown est repassé sous
    # reentry_drawdown (hystérésis), à reentry_scale de l'exposition le premier
    # mois, puis 100 %.
    reentry_drawdown: float = 0.10
    reentry_scale: float = 0.5
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
    """Facteur d'exposition global : target_vol / vol réalisée, plafonné à 1.

    Jamais de levier : le scalaire est borné à 1.0. C'est le vol-targeting
    continu de Barroso & Santa-Clara (rapport §1.2), pas un régime binaire.
    """
    if weights.empty:
        return 0.0
    returns = prices[weights.index].pct_change().iloc[-params.vol_lookback_days :]
    port_returns = returns.mul(weights, axis=1).sum(axis=1)
    realized = port_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    if realized == 0 or np.isnan(realized):
        return 0.0
    return min(1.0, params.target_annual_vol / realized)


def apply_risk_overlay(
    prices: pd.DataFrame, selected: pd.Series, params: RiskParams
) -> pd.Series:
    """Pipeline complet : inverse-vol → vol target (≤1) → plafond par position."""
    weights = inverse_vol_weights(prices, selected, params)
    scalar = portfolio_vol_scalar(prices, weights, params)
    return (weights * scalar).clip(upper=params.max_position_weight)


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
