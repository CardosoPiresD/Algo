"""Moteur de backtest : simulation à rebalancing périodique, coûts inclus.

Implémentation pandas/numpy volontairement simple et auditable (walk-forward,
pas de vectorisation opaque). vectorbt reste utilisable en complément pour des
études paramétriques massives (voir requirements-extra).

Piège évité (rapport §1.4, §3.5) : le signal à la date t n'utilise QUE des
données <= t (pas de look-ahead) ; les coûts de transaction sont appliqués sur
chaque rotation du portefeuille.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from hermes.strategy.momentum import (
    MomentumParams,
    rebalance_schedule,
    select_portfolio,
)
from hermes.strategy.risk import RiskParams, apply_risk_overlay


@dataclass
class BacktestConfig:
    initial_capital: float = 100_000.0
    commission_bps: float = 5.0
    slippage_bps: float = 5.0
    rebalance: str = "monthly"


@dataclass
class BacktestResult:
    equity_curve: pd.Series = field(default_factory=pd.Series)
    returns: pd.Series = field(default_factory=pd.Series)
    weights_history: pd.DataFrame = field(default_factory=pd.DataFrame)
    turnover: float = 0.0
    total_costs: float = 0.0

    @property
    def total_return(self) -> float:
        if self.equity_curve.empty:
            return 0.0
        return float(self.equity_curve.iloc[-1] / self.equity_curve.iloc[0] - 1)

    @property
    def max_drawdown(self) -> float:
        if self.equity_curve.empty:
            return 0.0
        peak = self.equity_curve.cummax()
        return float(((peak - self.equity_curve) / peak).max())


def run_backtest(
    prices: pd.DataFrame,
    momentum_params: MomentumParams,
    risk_params: RiskParams,
    config: BacktestConfig,
) -> BacktestResult:
    prices = prices.sort_index().dropna(how="all")
    daily_returns = prices.pct_change().fillna(0.0)
    schedule = rebalance_schedule(prices.index, config.rebalance)
    cost_rate = (config.commission_bps + config.slippage_bps) / 10_000.0

    current_weights = pd.Series(dtype=float)
    weights_records: dict[pd.Timestamp, pd.Series] = {}
    equity = config.initial_capital
    equity_points: dict[pd.Timestamp, float] = {}
    total_costs = 0.0
    turnover_sum = 0.0
    n_rebalances = 0

    warmup = momentum_params.lookback_months * 21 + 1

    for date in prices.index:
        if not current_weights.empty:
            day_ret = float(
                daily_returns.loc[date, current_weights.index]
                .mul(current_weights)
                .sum()
            )
            equity *= 1 + day_ret

        if date in schedule and len(prices.loc[:date]) >= warmup:
            window = prices.loc[:date]
            selected = select_portfolio(window, momentum_params)
            target = apply_risk_overlay(window, selected, risk_params)

            all_tickers = current_weights.index.union(target.index)
            old = current_weights.reindex(all_tickers, fill_value=0.0)
            new = target.reindex(all_tickers, fill_value=0.0)
            turnover = float((new - old).abs().sum())
            cost = equity * turnover * cost_rate
            equity -= cost
            total_costs += cost
            turnover_sum += turnover
            n_rebalances += 1

            current_weights = target[target > 0]
            weights_records[date] = current_weights

        equity_points[date] = equity

    equity_curve = pd.Series(equity_points).sort_index()
    returns = equity_curve.pct_change().dropna()
    return BacktestResult(
        equity_curve=equity_curve,
        returns=returns,
        weights_history=pd.DataFrame(weights_records).T,
        turnover=turnover_sum / n_rebalances if n_rebalances else 0.0,
        total_costs=total_costs,
    )
