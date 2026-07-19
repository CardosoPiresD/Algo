"""Moteur de backtest v2 : simulation quotidienne via le cœur decide() partagé.

Correction structurante (CM-1, docs/HERMES_V2_ROADMAP.md) : le backtest appelle
exactement les mêmes fonctions de décision que la production —
`decide_daily` (stops reduce-only + coupe-circuit) chaque jour,
`decide_rebalance` (momentum ∩ TSMOM + overlay + ré-entrée) aux dates de
rebalancement. Les trailing stops, le coupe-circuit et la règle de ré-entrée
sont donc SIMULÉS, plus seulement déclarés (bug v1 corrigé).

Pièges évités (rapport §1.4, §3.5) : le signal à la date t n'utilise que des
données <= t ; les coûts de transaction s'appliquent à chaque rotation, stops
inclus.
"""

from dataclasses import dataclass, field

import pandas as pd

from hermes.strategy.decide import PortfolioState, decide_daily, decide_rebalance
from hermes.strategy.momentum import MomentumParams, rebalance_schedule
from hermes.strategy.risk import RiskParams


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
    n_stop_sales: int = 0
    n_breaker_events: int = 0
    reentry_events: int = 0

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


def _transition_cost(
    old: dict, new: dict, equity: float, cost_rate: float
) -> tuple[float, float]:
    tickers = set(old) | set(new)
    turnover = sum(abs(new.get(t, 0.0) - old.get(t, 0.0)) for t in tickers)
    return turnover, equity * turnover * cost_rate


def run_backtest(
    prices: pd.DataFrame,
    momentum_params: MomentumParams,
    risk_params: RiskParams,
    config: BacktestConfig,
) -> BacktestResult:
    prices = prices.sort_index().dropna(how="all")
    daily_returns = prices.pct_change().fillna(0.0)
    schedule = set(rebalance_schedule(prices.index, config.rebalance))
    cost_rate = (config.commission_bps + config.slippage_bps) / 10_000.0
    warmup = momentum_params.lookback_months * 21 + 1

    state = PortfolioState(nav=config.initial_capital, nav_peak=config.initial_capital)
    equity = config.initial_capital
    equity_points: dict[pd.Timestamp, float] = {}
    weights_records: dict[pd.Timestamp, pd.Series] = {}
    total_costs = 0.0
    turnover_sum = 0.0
    n_rebalances = 0
    n_stop_sales = 0
    n_breaker = 0
    n_reentry = 0

    for date in prices.index:
        # 1. Rendement du jour sur les positions détenues
        if state.holdings:
            day_ret = sum(
                float(daily_returns.at[date, t]) * w for t, w in state.holdings.items()
            )
            equity *= 1 + day_ret

        # 2. Décision quotidienne : stops + coupe-circuit (reduce-only)
        pre_holdings = dict(state.holdings)
        daily = decide_daily(prices.loc[date], equity, state, risk_params)
        state = daily.state
        if daily.stop_sales:
            n_stop_sales += len(daily.stop_sales)
            turnover, cost = _transition_cost(
                pre_holdings, state.holdings, equity, cost_rate
            )
            equity -= cost
            total_costs += cost
        if daily.breaker_triggered_today:
            n_breaker += 1

        # 3. Rebalancement aux dates prévues (après warmup)
        if date in schedule and len(prices.loc[:date]) >= warmup:
            window = prices.loc[:date]
            pre_holdings = dict(state.holdings)
            decision = decide_rebalance(
                window, state, momentum_params, risk_params
            )
            state = decision.state
            if decision.reason == "reentry_50":
                n_reentry += 1
            turnover, cost = _transition_cost(
                pre_holdings, state.holdings, equity, cost_rate
            )
            equity -= cost
            total_costs += cost
            turnover_sum += turnover
            n_rebalances += 1
            weights_records[date] = pd.Series(state.holdings, dtype=float)

        # 4. NAV du jour (l'état porte le même chiffre que la production)
        from dataclasses import replace as _replace

        state = _replace(state, nav=equity, nav_peak=max(state.nav_peak, equity))
        equity_points[date] = equity

    equity_curve = pd.Series(equity_points).sort_index()
    returns = equity_curve.pct_change().dropna()
    return BacktestResult(
        equity_curve=equity_curve,
        returns=returns,
        weights_history=pd.DataFrame(weights_records).T,
        turnover=turnover_sum / n_rebalances if n_rebalances else 0.0,
        total_costs=total_costs,
        n_stop_sales=n_stop_sales,
        n_breaker_events=n_breaker,
        reentry_events=n_reentry,
    )
