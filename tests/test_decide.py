"""Tests du cœur de décision pur (CM-1) : stops, breaker, ré-entrée."""

import numpy as np
import pandas as pd

from hermes.strategy.decide import (
    PortfolioState,
    decide_daily,
    decide_rebalance,
)
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams


RISK = RiskParams(
    trailing_stop_pct=0.15,
    max_drawdown_circuit_breaker=0.15,
    reentry_drawdown=0.10,
    reentry_scale=0.5,
)


def make_window(n_days=300, trends=None, seed=5):
    trends = trends or {f"T{i}": 0.0008 for i in range(12)}
    dates = pd.bdate_range("2022-01-03", periods=n_days)
    rng = np.random.default_rng(seed)
    data = {
        k: 100 * np.exp(np.cumsum(rng.normal(drift, 0.01, n_days)))
        for k, drift in trends.items()
    }
    return pd.DataFrame(data, index=dates)


def test_daily_updates_highs():
    state = PortfolioState(holdings={"A": 0.5}, highs={"A": 100.0}, nav=1000, nav_peak=1000)
    d = decide_daily(pd.Series({"A": 110.0}), 1010, state, RISK)
    assert d.state.highs["A"] == 110.0
    assert d.stop_sales == ()


def test_daily_trailing_stop_sells():
    state = PortfolioState(holdings={"A": 0.5}, highs={"A": 100.0}, nav=1000, nav_peak=1000)
    d = decide_daily(pd.Series({"A": 84.0}), 950, state, RISK)
    assert "A" in d.stop_sales
    assert "A" not in d.state.holdings
    assert "A" not in d.state.highs


def test_daily_is_reduce_only():
    """decide_daily ne peut jamais AJOUTER une position."""
    state = PortfolioState(holdings={"A": 0.5}, highs={"A": 100.0}, nav=1000, nav_peak=1000)
    d = decide_daily(pd.Series({"A": 101.0, "B": 50.0}), 1005, state, RISK)
    assert set(d.state.holdings) <= {"A"}


def test_daily_breaker_liquidates_and_blocks():
    state = PortfolioState(
        holdings={"A": 0.5, "B": 0.4},
        highs={"A": 100.0, "B": 50.0},
        nav=1000,
        nav_peak=1000,
    )
    d = decide_daily(pd.Series({"A": 99.0, "B": 49.0}), 840, state, RISK)
    assert d.breaker_triggered_today
    assert d.state.breaker_active
    assert d.state.holdings == {}
    assert set(d.stop_sales) == {"A", "B"}


def test_rebalance_breaker_hold_stays_in_cash():
    window = make_window()
    state = PortfolioState(nav=850, nav_peak=1000, breaker_active=True)
    decision = decide_rebalance(window, state, MomentumParams(top_n=3), RISK)
    assert decision.reason == "breaker_hold"
    assert decision.target_weights == {}
    assert decision.state.breaker_active


def test_rebalance_reentry_sequence():
    """Breaker actif + drawdown < 10% -> ré-entrée à 50%, puis 100% au cycle suivant."""
    window = make_window()
    state = PortfolioState(nav=950, nav_peak=1000, breaker_active=True)
    d1 = decide_rebalance(window, state, MomentumParams(top_n=3), RISK)
    assert d1.reason == "reentry_50"
    assert not d1.state.breaker_active
    assert d1.state.reentry_scale == 0.5
    assert d1.target_weights  # ré-investi

    full = decide_rebalance(window, d1.state, MomentumParams(top_n=3), RISK)
    assert full.reason == "reentry_full"
    assert full.state.reentry_scale == 1.0
    # Même fenêtre de prix: les poids 100% doivent être ~2x les poids 50%
    for t, w in d1.target_weights.items():
        assert abs(full.target_weights[t] - 2 * w) < 1e-9


def test_rebalance_veto_goes_to_cash_never_replaced():
    window = make_window()
    params = MomentumParams(top_n=3)
    base = decide_rebalance(window, PortfolioState(nav=1000, nav_peak=1000), params, RISK)
    top = list(base.target_weights)
    vetoed_ticker = top[0]
    vetoed = decide_rebalance(
        window,
        PortfolioState(nav=1000, nav_peak=1000),
        params,
        RISK,
        vetoed=frozenset({vetoed_ticker}),
    )
    assert vetoed_ticker not in vetoed.target_weights
    # Jamais de remplacement n+1: le nombre de positions DIMINUE
    assert len(vetoed.target_weights) == len(base.target_weights) - 1
    # Et le poids total baisse (le poids du veto part au cash)
    assert sum(vetoed.target_weights.values()) < sum(base.target_weights.values())


def test_rebalance_initializes_highs_for_new_entries():
    window = make_window()
    decision = decide_rebalance(
        window, PortfolioState(nav=1000, nav_peak=1000), MomentumParams(top_n=3), RISK
    )
    for t in decision.target_weights:
        assert t in decision.state.highs
        assert decision.state.highs[t] == float(window.iloc[-1][t])
