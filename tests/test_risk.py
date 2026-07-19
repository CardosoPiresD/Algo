import numpy as np
import pandas as pd

from hermes.strategy.risk import (
    RiskParams,
    apply_risk_overlay,
    circuit_breaker_triggered,
    inverse_vol_weights,
    kill_switch_active,
    portfolio_vol_scalar,
    trailing_stop_triggered,
)


def make_prices(vols={"LOWVOL": 0.005, "HIGHVOL": 0.03}, n_days=120):
    dates = pd.bdate_range("2023-01-02", periods=n_days)
    rng = np.random.default_rng(11)
    data = {
        name: 100 * np.exp(np.cumsum(rng.normal(0.0005, vol, n_days)))
        for name, vol in vols.items()
    }
    return pd.DataFrame(data, index=dates)


def test_inverse_vol_overweights_low_vol():
    prices = make_prices()
    selected = pd.Series(0.5, index=["LOWVOL", "HIGHVOL"])
    weights = inverse_vol_weights(prices, selected, RiskParams(max_position_weight=1.0))
    assert weights["LOWVOL"] > weights["HIGHVOL"]


def test_max_position_weight_cap():
    prices = make_prices()
    selected = pd.Series(0.5, index=["LOWVOL", "HIGHVOL"])
    params = RiskParams(max_position_weight=0.15)
    weights = apply_risk_overlay(prices, selected, params)
    assert (weights <= 0.15 + 1e-9).all()


def test_vol_scalar_never_levers_up():
    prices = make_prices(vols={"A": 0.001, "B": 0.001})
    weights = pd.Series(0.5, index=["A", "B"])
    scalar = portfolio_vol_scalar(prices, weights, RiskParams())
    assert scalar <= 1.0 + 1e-9


def test_no_kelly_pretense():
    """v2: le pseudo demi-Kelly (no-op ×0.5×2) a été retiré — RiskParams ne
    doit plus exposer de kelly_fraction."""
    assert not hasattr(RiskParams(), "kelly_fraction")


def test_empty_selection_passthrough():
    prices = make_prices()
    empty = pd.Series(dtype=float)
    assert apply_risk_overlay(prices, empty, RiskParams()).empty


def test_trailing_stop():
    params = RiskParams(trailing_stop_pct=0.15)
    assert trailing_stop_triggered(100.0, 84.0, params)
    assert not trailing_stop_triggered(100.0, 90.0, params)


def test_circuit_breaker():
    params = RiskParams(max_drawdown_circuit_breaker=0.15)
    crash = pd.Series([100, 110, 90.0])
    ok = pd.Series([100, 105, 102.0])
    assert circuit_breaker_triggered(crash, params)
    assert not circuit_breaker_triggered(ok, params)


def test_kill_switch(tmp_path):
    params = RiskParams(kill_switch_file="KILL_SWITCH")
    assert not kill_switch_active(params, str(tmp_path))
    (tmp_path / "KILL_SWITCH").touch()
    assert kill_switch_active(params, str(tmp_path))
