import numpy as np
import pandas as pd

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.validate import (
    deflated_sharpe_ratio,
    probability_of_backtest_overfitting,
    sharpe_ratio,
    validate_strategy,
)
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams


def make_market(n_days=600, n_assets=6, seed=3):
    dates = pd.bdate_range("2021-01-04", periods=n_days)
    rng = np.random.default_rng(seed)
    data = {}
    for i in range(n_assets):
        drift = 0.0008 if i < n_assets // 2 else -0.0003
        data[f"T{i}"] = 100 * np.exp(np.cumsum(rng.normal(drift, 0.012, n_days)))
    return pd.DataFrame(data, index=dates)


def test_backtest_runs_and_produces_equity_curve():
    prices = make_market()
    result = run_backtest(
        prices,
        MomentumParams(top_n=2),
        RiskParams(),
        BacktestConfig(initial_capital=100_000),
    )
    assert len(result.equity_curve) == len(prices)
    assert result.equity_curve.iloc[0] == 100_000
    assert not result.weights_history.empty


def test_backtest_costs_reduce_equity():
    prices = make_market()
    free = run_backtest(
        prices,
        MomentumParams(top_n=2),
        RiskParams(),
        BacktestConfig(commission_bps=0, slippage_bps=0),
    )
    costly = run_backtest(
        prices,
        MomentumParams(top_n=2),
        RiskParams(),
        BacktestConfig(commission_bps=50, slippage_bps=50),
    )
    assert costly.total_costs > 0
    assert costly.equity_curve.iloc[-1] < free.equity_curve.iloc[-1]


def test_sharpe_of_positive_drift_is_positive():
    rng = np.random.default_rng(1)
    good = pd.Series(rng.normal(0.001, 0.01, 500))
    assert sharpe_ratio(good) > 0


def test_deflated_sharpe_penalizes_many_trials():
    rng = np.random.default_rng(2)
    returns = pd.Series(rng.normal(0.0005, 0.01, 500))
    dsr_few = deflated_sharpe_ratio(returns, n_trials=1)
    dsr_many = deflated_sharpe_ratio(returns, n_trials=1000)
    assert dsr_many < dsr_few


def test_pbo_high_for_pure_noise():
    rng = np.random.default_rng(4)
    trials = pd.DataFrame(rng.normal(0, 0.01, (400, 20)))
    pbo = probability_of_backtest_overfitting(trials)
    assert pbo > 0.3


def test_pbo_low_for_one_dominant_strategy():
    rng = np.random.default_rng(5)
    noise = rng.normal(0, 0.01, (400, 19))
    winner = rng.normal(0.005, 0.01, (400, 1))
    trials = pd.DataFrame(np.hstack([winner, noise]))
    pbo = probability_of_backtest_overfitting(trials)
    assert pbo < 0.2


def test_validate_strategy_verdict_structure():
    rng = np.random.default_rng(6)
    returns = pd.Series(rng.normal(0.002, 0.008, 500))
    verdict = validate_strategy(returns, n_trials=1)
    assert set(verdict) >= {
        "sharpe",
        "deflated_sharpe_prob",
        "dsr_pass",
        "approved_for_paper",
    }


def test_noise_strategy_not_approved():
    rng = np.random.default_rng(8)
    returns = pd.Series(rng.normal(0.0, 0.01, 500))
    verdict = validate_strategy(returns, n_trials=100)
    assert not verdict["approved_for_paper"]
