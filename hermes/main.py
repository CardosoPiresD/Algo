"""Hermes — point d'entrée.

Modes:
  python -m hermes.main backtest    # backtest + validation anti-overfitting
  python -m hermes.main paper       # un cycle de rebalancing en paper trading
  python -m hermes.main paper --dry-run   # calcule les ordres sans les envoyer
"""

import argparse
import json
import sys

import pandas as pd
import yaml

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.validate import validate_strategy
from hermes.data.ingestion import fetch_history_yfinance
from hermes.reporting.tearsheet import summary_metrics
from hermes.strategy.momentum import MomentumParams, select_portfolio
from hermes.strategy.risk import RiskParams, apply_risk_overlay


def load_settings(path: str = "hermes/config/settings.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_params(cfg: dict) -> tuple[MomentumParams, RiskParams]:
    s, r = cfg["strategy"], cfg["risk"]
    momentum = MomentumParams(
        lookback_months=s["lookback_months"],
        skip_months=s["skip_months"],
        top_n=s["top_n"],
        tsmom_filter=s["tsmom_filter"],
    )
    risk = RiskParams(
        vol_lookback_days=r["vol_lookback_days"],
        target_annual_vol=r["target_annual_vol"],
        max_position_weight=r["max_position_weight"],
        kelly_fraction=r["kelly_fraction"],
        trailing_stop_pct=r["trailing_stop_pct"],
        max_drawdown_circuit_breaker=r["max_drawdown_circuit_breaker"],
        kill_switch_file=r["kill_switch_file"],
    )
    return momentum, risk


def cmd_backtest(cfg: dict) -> int:
    bt = cfg["backtest"]
    momentum, risk = build_params(cfg)
    print(f"Téléchargement de {len(cfg['universe']['tickers'])} tickers…")
    prices = fetch_history_yfinance(
        cfg["universe"]["tickers"], start=bt["start"], end=bt.get("end")
    )
    print(f"Données: {prices.shape[0]} jours × {prices.shape[1]} titres")

    result = run_backtest(
        prices,
        momentum,
        risk,
        BacktestConfig(
            initial_capital=bt["initial_capital"],
            commission_bps=bt["commission_bps"],
            slippage_bps=bt["slippage_bps"],
            rebalance=cfg["strategy"]["rebalance"],
        ),
    )
    metrics = summary_metrics(result.returns)
    print("\n=== Backtest ===")
    print(json.dumps(metrics, indent=2))
    print(f"Turnover moyen/rebalance: {result.turnover:.2%}")
    print(f"Coûts totaux: {result.total_costs:,.0f}")

    v = cfg["validation"]
    verdict = validate_strategy(
        result.returns,
        n_trials=v["n_trials"],
        min_dsr_prob=v["min_deflated_sharpe_prob"],
        max_pbo=v["max_pbo"],
    )
    print("\n=== Validation anti-overfitting ===")
    print(json.dumps(verdict, indent=2))
    if not verdict["approved_for_paper"]:
        print(
            "\n⛔ NON APPROUVÉ pour le paper trading — le Sharpe observé n'est pas "
            "distinguable d'un artefact de sélection au seuil configuré."
        )
        return 1
    print("\n✅ Approuvé pour le paper trading.")
    return 0


def cmd_paper(cfg: dict, dry_run: bool) -> int:
    from hermes.execution.ibkr_client import IBKRClient
    from hermes.execution.order_manager import OrderManager

    momentum, risk = build_params(cfg)
    ex = cfg["execution"]
    client = IBKRClient(
        host=ex["ibkr"]["host"],
        port=ex["ibkr"]["port"],
        client_id=ex["ibkr"]["client_id"],
        account_type=ex["account_type"],
        max_messages_per_second=ex["max_messages_per_second"],
    )
    client.connect()
    try:
        from hermes.data.ingestion import IBKRHistoryFetcher

        fetcher = IBKRHistoryFetcher(client.ib)
        prices = fetcher.fetch_universe(cfg["universe"]["tickers"])
        if prices.empty:
            print("Aucune donnée reçue d'IBKR — abandon.")
            return 1

        selected = select_portfolio(prices, momentum)
        target = apply_risk_overlay(prices, selected, risk)
        print(f"Portefeuille cible:\n{target}")

        manager = OrderManager(client, risk)
        equity_curve = pd.Series([client.net_liquidation()])
        executed = manager.execute(
            target, prices.iloc[-1], equity_curve, dry_run=dry_run
        )
        print(f"{len(executed)} ordres {'calculés (dry-run)' if dry_run else 'envoyés'}.")
        return 0
    finally:
        client.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(prog="hermes")
    parser.add_argument("mode", choices=["backtest", "paper"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", default="hermes/config/settings.yaml")
    args = parser.parse_args()

    cfg = load_settings(args.config)
    if args.mode == "backtest":
        return cmd_backtest(cfg)
    return cmd_paper(cfg, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
