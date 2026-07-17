import numpy as np
import pandas as pd
import pytest

from hermes.strategy.momentum import (
    MomentumParams,
    momentum_score,
    rebalance_schedule,
    select_portfolio,
)


def make_prices(n_days=300, trends=None):
    dates = pd.bdate_range("2022-01-03", periods=n_days)
    trends = trends or {"UP": 0.001, "FLAT": 0.0, "DOWN": -0.001}
    rng = np.random.default_rng(7)
    data = {}
    for name, drift in trends.items():
        noise = rng.normal(0, 0.002, n_days)
        data[name] = 100 * np.exp(np.cumsum(drift + noise))
    return pd.DataFrame(data, index=dates)


def test_momentum_score_ranks_trend():
    prices = make_prices()
    params = MomentumParams(lookback_months=12, skip_months=1, top_n=2)
    scores = momentum_score(prices, params)
    assert scores["UP"] > scores["FLAT"] > scores["DOWN"]


def test_momentum_score_insufficient_history_raises():
    prices = make_prices(n_days=50)
    with pytest.raises(ValueError):
        momentum_score(prices, MomentumParams())


def test_select_portfolio_tsmom_filter_excludes_negative():
    prices = make_prices()
    params = MomentumParams(top_n=3, tsmom_filter=True)
    weights = select_portfolio(prices, params)
    assert "DOWN" not in weights.index
    assert "UP" in weights.index


def test_select_portfolio_weights_sum_below_one_with_filter():
    prices = make_prices(trends={"D1": -0.001, "D2": -0.002, "U1": 0.001})
    params = MomentumParams(top_n=3, tsmom_filter=True)
    weights = select_portfolio(prices, params)
    assert weights.sum() <= 1.0 + 1e-9
    assert len(weights) == 1


def test_select_portfolio_all_negative_returns_empty():
    prices = make_prices(trends={"D1": -0.002, "D2": -0.003})
    weights = select_portfolio(prices, MomentumParams(top_n=2, tsmom_filter=True))
    assert weights.empty


def test_rebalance_schedule_monthly_is_month_ends():
    dates = pd.bdate_range("2023-01-02", "2023-06-30")
    schedule = rebalance_schedule(dates, "monthly")
    assert len(schedule) == 6
    assert all(d in dates for d in schedule)


def test_no_lookahead_score_uses_only_past_window():
    prices = make_prices(n_days=320)
    params = MomentumParams()
    cutoff = prices.index[280]
    window = prices.loc[:cutoff]
    s1 = momentum_score(window, params)
    prices_mutated = prices.copy()
    prices_mutated.iloc[281:] *= 5.0
    s2 = momentum_score(prices_mutated.loc[:cutoff], params)
    pd.testing.assert_series_equal(s1, s2)
