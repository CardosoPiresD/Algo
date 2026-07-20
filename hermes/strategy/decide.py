"""Cœur de décision unique — CM-1 de la roadmap (docs/HERMES_V2_ROADMAP.md).

Fonctions PURES appelées à l'identique par le backtest (`backtest/engine.py`)
et la production (`ops/daily_check.py`, supervisor). Aucune I/O, aucun accès
broker, aucun appel réseau : entrées → décision. C'est ce qui supprime la
divergence silencieuse recherche/production.

Granularité :
- `decide_daily`   — chaque jour de bourse : mise à jour des plus-hauts,
  trailing stops (reduce-only par construction), coupe-circuit de drawdown.
- `decide_rebalance` — aux dates de rebalancement : momentum ∩ TSMOM, vetos
  mécaniques, overlay de risque, règle de ré-entrée pré-enregistrée.
"""

from dataclasses import dataclass, field, replace

import pandas as pd

from hermes.strategy.momentum import MomentumParams, select_portfolio
from hermes.strategy.risk import (
    RiskParams,
    apply_risk_overlay,
    trailing_stop_triggered,
)


@dataclass(frozen=True)
class PortfolioState:
    """État minimal du portefeuille, persisté entre les cycles.

    holdings : ticker -> poids cible détenu.
    highs    : ticker -> plus haut cours de clôture depuis l'entrée (stops).
    nav / nav_peak : valeur liquidative courante et son plus haut historique.
    breaker_active : coupe-circuit déclenché (plus d'achats).
    reentry_scale  : 1.0 en régime normal ; après ré-entrée post-breaker,
                     vaut RiskParams.reentry_scale pendant un cycle.
    """

    holdings: dict = field(default_factory=dict)
    highs: dict = field(default_factory=dict)
    nav: float = 0.0
    nav_peak: float = 0.0
    breaker_active: bool = False
    reentry_scale: float = 1.0

    @property
    def drawdown(self) -> float:
        if self.nav_peak <= 0:
            return 0.0
        return max(0.0, (self.nav_peak - self.nav) / self.nav_peak)


@dataclass(frozen=True)
class DailyDecision:
    state: PortfolioState
    stop_sales: tuple = ()          # tickers vendus par trailing stop
    breaker_triggered_today: bool = False


@dataclass(frozen=True)
class RebalanceDecision:
    state: PortfolioState
    target_weights: dict = field(default_factory=dict)
    reason: str = "normal"          # normal | breaker_hold | reentry_50 | reentry_full


def decide_daily(
    close_today: pd.Series,
    nav_today: float,
    state: PortfolioState,
    risk: RiskParams,
) -> DailyDecision:
    """Décision quotidienne : plus-hauts, stops (reduce-only), coupe-circuit.

    close_today : cours de clôture du jour (au moins les tickers détenus).
    nav_today   : NAV du portefeuille en clôture.
    Reduce-only par construction : cette fonction ne peut que retirer des
    positions, jamais en ajouter (même asymétrie que la couche IA).
    """
    nav_peak = max(state.nav_peak, nav_today)
    holdings = dict(state.holdings)
    highs = dict(state.highs)
    stop_sales = []

    for ticker in list(holdings):
        price = close_today.get(ticker)
        if price is None or pd.isna(price) or price <= 0:
            continue
        highs[ticker] = max(highs.get(ticker, price), float(price))
        if trailing_stop_triggered(highs[ticker], float(price), risk):
            stop_sales.append(ticker)
            del holdings[ticker]
            del highs[ticker]

    drawdown = (nav_peak - nav_today) / nav_peak if nav_peak > 0 else 0.0
    breaker_today = (
        not state.breaker_active
        and drawdown >= risk.max_drawdown_circuit_breaker
    )
    breaker_active = state.breaker_active or breaker_today
    if breaker_today:
        # Coupe-circuit : liquidation totale (cristallise, la ré-entrée
        # pré-enregistrée borne le dégât comportemental — design v2 §5/§9.3).
        stop_sales.extend(t for t in holdings if t not in stop_sales)
        holdings = {}
        highs = {}

    new_state = replace(
        state,
        holdings=holdings,
        highs=highs,
        nav=nav_today,
        nav_peak=nav_peak,
        breaker_active=breaker_active,
    )
    return DailyDecision(
        state=new_state,
        stop_sales=tuple(stop_sales),
        breaker_triggered_today=breaker_today,
    )


def decide_rebalance(
    prices_window: pd.DataFrame,
    state: PortfolioState,
    momentum: MomentumParams,
    risk: RiskParams,
    vetoed: frozenset = frozenset(),
    selector=None,
) -> RebalanceDecision:
    """Décision de rebalancement mensuel.

    prices_window : historique de prix ajustés se terminant à la date de
    décision (le moteur garantit l'absence de look-ahead).
    vetoed : tickers exclus par les flags mécaniques 8-K (et, plus tard, par la
    sentinelle IA promue). Le poids d'un titre veto va au cash — jamais de
    remplacement par le rang n+1 (design v2 §3.1).
    selector : hook de sélection alternatif (callable(prices_window, momentum)
    -> Series de poids), utilisé UNIQUEMENT par le banc de validation (test de
    permutation QW-10b) pour éviter une seconde implémentation du pipeline.
    Défaut : la sélection momentum réelle.
    """
    if state.breaker_active:
        if state.drawdown >= risk.reentry_drawdown:
            # Toujours en zone rouge : on reste en cash, pas d'achats.
            return RebalanceDecision(state=state, target_weights={}, reason="breaker_hold")
        # Hystérésis franchie : ré-entrée pré-enregistrée à exposition réduite.
        scale = risk.reentry_scale
        new_state = replace(state, breaker_active=False, reentry_scale=scale)
        reason = "reentry_50"
    elif state.reentry_scale < 1.0:
        # Cycle suivant la ré-entrée : retour à pleine exposition.
        new_state = replace(state, reentry_scale=1.0)
        scale = 1.0
        reason = "reentry_full"
    else:
        new_state = state
        scale = 1.0
        reason = "normal"

    select = selector if selector is not None else select_portfolio
    selected = select(prices_window, momentum)
    if not selected.empty and vetoed:
        kept = [t for t in selected.index if t not in vetoed]
        selected = selected.loc[kept]  # le poids des vetos part au cash

    target = apply_risk_overlay(prices_window, selected, risk) * scale
    target = target[target > 0]

    last_close = prices_window.iloc[-1]
    holdings = {t: float(w) for t, w in target.items()}
    highs = {
        t: float(state.highs.get(t, last_close[t]))
        for t in holdings
        if t in last_close and not pd.isna(last_close[t])
    }
    final_state = replace(new_state, holdings=holdings, highs=highs)
    return RebalanceDecision(state=final_state, target_weights=holdings, reason=reason)
