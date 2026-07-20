"""Hermes — point d'entrée.

Modes:
  python -m hermes.main backtest          # backtest + validation anti-overfitting
  python -m hermes.main paper [--dry-run] # un cycle de rebalancing paper
  python -m hermes.main daily [--dry-run] # job quotidien: NAV, stops, breaker

Correction v2 : le coupe-circuit est branché sur l'historique NAV persistant
(state/nav_history.csv) — plus jamais sur une série à un point (bug v1).
"""

import argparse
import json
import sys

import pandas as pd
import yaml

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.validate import validate_strategy
from hermes.data.ingestion import fetch_history_yfinance
from hermes.ops.state import StateStore
from hermes.reporting.tearsheet import summary_metrics
from hermes.research.trials import TrialsRegistry, data_hash
from hermes.strategy.decide import decide_daily, decide_rebalance
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams


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
        trailing_stop_pct=r["trailing_stop_pct"],
        max_drawdown_circuit_breaker=r["max_drawdown_circuit_breaker"],
        reentry_drawdown=r.get("reentry_drawdown", 0.10),
        reentry_scale=r.get("reentry_scale", 0.5),
        kill_switch_file=r["kill_switch_file"],
    )
    return momentum, risk


def fetch_risk_free(start: str, end: str | None) -> pd.Series | float:
    """T-Bill 3 mois via ^IRX (annualisé, en %) — QW-1. Fallback honnête: 0."""
    try:
        irx = fetch_history_yfinance(["^IRX"], start=start, end=end)
        if irx.empty:
            raise ValueError("^IRX vide")
        return irx.iloc[:, 0] / 100.0
    except Exception as exc:  # réseau bloqué, ticker indisponible…
        print(f"⚠️  Taux sans risque indisponible ({exc}) — rf=0, Sharpe optimiste.")
        return 0.0


def cmd_backtest(cfg: dict) -> int:
    bt = cfg["backtest"]
    momentum, risk = build_params(cfg)
    print(f"Téléchargement de {len(cfg['universe']['tickers'])} tickers…")
    prices = fetch_history_yfinance(
        cfg["universe"]["tickers"], start=bt["start"], end=bt.get("end")
    )
    print(f"Données: {prices.shape[0]} jours × {prices.shape[1]} titres")
    print(
        "⚠️  Univers = liste ACTUELLE (survivorship bias) tant que le CSV "
        "point-in-time n'est pas construit (QW-2) — résultat optimiste."
    )
    risk_free = fetch_risk_free(bt["start"], bt.get("end"))

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
    print(
        f"Stops déclenchés: {result.n_stop_sales} · breaker: "
        f"{result.n_breaker_events} · ré-entrées: {result.reentry_events}"
    )

    # QW-8 : enregistrement mécanique de l'essai AVANT le calcul du verdict —
    # ce run compte dans n_trials, y compris pour lui-même.
    registry = TrialsRegistry()
    strategy_config = {**cfg["strategy"], **cfg["risk"], **{"universe": cfg["universe"]["tickers"]}}
    registry.record(
        config=strategy_config,
        metrics={**metrics, "max_drawdown": result.max_drawdown},
        data_h=data_hash(prices),
        hypothese=cfg.get("validation", {}).get("hypothese"),
    )

    v = cfg["validation"]
    verdict = validate_strategy(
        result.returns,
        min_dsr_prob=v["min_deflated_sharpe_prob"],
        max_pbo=v["max_pbo"],
        risk_free_annual=risk_free,
        registry=registry,
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


def _connect(cfg: dict):
    from hermes.execution.ibkr_client import IBKRClient

    ex = cfg["execution"]
    client = IBKRClient(
        host=ex["ibkr"]["host"],
        port=ex["ibkr"]["port"],
        client_id=ex["ibkr"]["client_id"],
        account_type=ex["account_type"],
        max_messages_per_second=ex["max_messages_per_second"],
    )
    client.connect()
    return client


def fetch_mechanical_flags(cfg: dict, tickers: list[str]):
    """Flags 8-K mécaniques — fail-open : erreur => aucun flag, état journalisé."""
    from hermes.intel.mechanical_flags import FlagsReport, scan_8k_flags

    intel_cfg = cfg.get("intel", {})
    if not intel_cfg.get("flags_enabled", False):
        return FlagsReport()
    try:
        from hermes.intel.edgar_client import EdgarClient

        client = EdgarClient(user_agent=intel_cfg["edgar_user_agent"])
        report = scan_8k_flags(tickers, client)
        errors = [t for t, s in report.status.items() if s == "erreur"]
        if errors:
            print(f"⚠️  EDGAR en erreur pour {errors} — flags partiels (fail-open).")
        if report.vetoed:
            print(f"⛔ Vetos mécaniques 8-K (1.03/4.02): {sorted(report.vetoed)}")
        return report
    except Exception as exc:
        print(f"⚠️  Couche flags indisponible ({exc}) — cycle quant pur (fail-open).")
        return FlagsReport(status={t: "erreur" for t in tickers})


def run_ai_observation(cfg: dict, tickers: list[str]) -> None:
    """Couche IA en observation stricte — n'a AUCUN effet sur le trading.

    Fail-open total : clé absente, budget épuisé, réseau ou parse en erreur =>
    on enregistre l'état et on continue. Aucun retour n'influence les ordres.
    """
    ai_cfg = cfg.get("ai", {})
    if not ai_cfg.get("enabled", False):
        return
    try:
        from hermes.ai.budget_guard import BudgetGuard
        from hermes.ai.client import LLMClient, MeteredClient
        from hermes.intel.company_analysis import analyze_company, save_assessments
        from hermes.intel.edgar_client import EdgarClient
        from hermes.intel.edgar_filings import FilingReader
        from hermes.intel.sentinel_ai import assess_going_concern

        base_client = LLMClient(
            model=ai_cfg["model"],
            base_url=ai_cfg["base_url"],
            api_key_env=ai_cfg["api_key_env"],
        )
        if not base_client.available:
            print("ℹ️  Couche IA inactive (clé absente) — quant pur, aucun impact.")
            return

        month = pd.Timestamp.now().strftime("%Y-%m")
        budget = BudgetGuard(
            monthly_cap_eur=ai_cfg["budget_cap_eur"],
            price_in_per_mtok=ai_cfg["price_in_per_mtok"],
            price_out_per_mtok=ai_cfg["price_out_per_mtok"],
        )
        if not budget.can_spend(month):
            print(f"ℹ️  Budget IA du mois épuisé ({budget.spent(month):.2f} €) — quant pur.")
            return
        client = MeteredClient(base_client, budget, month)

        edgar = EdgarClient(user_agent=cfg["intel"]["edgar_user_agent"])
        reader = FilingReader(edgar)
        cik_map = edgar.ticker_to_cik()
        assessments = []
        limit = ai_cfg.get("max_companies_per_cycle", 12)

        for ticker in tickers[:limit]:
            if not client.available:
                break
            cik = cik_map.get(ticker.upper())
            if cik is None:
                continue
            filing = reader.latest_filing_text(cik)
            text = filing["text"] if filing else None

            if ai_cfg.get("run_sentinel", True):
                v = assess_going_concern(ticker, text, client)
                if v.is_valid_grave:
                    print(
                        f"👁️  [SHADOW] Sentinelle IA: {ticker} classé GRAVE "
                        f"({v.categorie}) — enregistré, AUCUNE action."
                    )
            if ai_cfg.get("run_company_analysis", True):
                assessments.append(analyze_company(ticker, text, client))

        if assessments:
            path = save_assessments(assessments, month)
            print(f"👁️  [OBSERVATION] Analyses d'entreprise enregistrées: {path}")
        print(f"ℹ️  Dépense IA cumulée ce mois: {budget.spent(month):.3f} €")
    except Exception as exc:
        print(f"⚠️  Couche IA indisponible ({exc}) — sans effet, quant pur (fail-open).")


def cmd_paper(cfg: dict, dry_run: bool) -> int:
    """Cycle de rebalancement mensuel en paper trading."""
    from hermes.data.ingestion import IBKRHistoryFetcher
    from hermes.execution.order_manager import OrderManager
    from hermes.ops.decision_journal import build_decision_journal, save_decision_journal

    momentum, risk = build_params(cfg)
    store = StateStore()
    client = _connect(cfg)
    try:
        fetcher = IBKRHistoryFetcher(client.ib)
        prices = fetcher.fetch_universe(cfg["universe"]["tickers"])
        if prices.empty:
            print("Aucune donnée reçue d'IBKR — abandon (fail-closed).")
            return 1

        state = store.load_portfolio()
        nav = client.net_liquidation()
        nav_history = store.append_nav(prices.index[-1], nav)
        from dataclasses import replace

        state = replace(state, nav=nav, nav_peak=max(state.nav_peak, nav))

        flags = fetch_mechanical_flags(cfg, list(prices.columns))
        decision = decide_rebalance(
            prices, state, momentum, risk, vetoed=flags.vetoed
        )
        target = pd.Series(decision.target_weights, dtype=float)
        print(f"Décision: {decision.reason}\nPortefeuille cible:\n{target}")

        journal = build_decision_journal(
            prices, state, decision, momentum, risk, vetoed=flags.vetoed
        )
        journal_path = save_decision_journal(journal)
        print(f"Journal de décision: {journal_path}")

        # Couche IA — OBSERVATION STRICTE : lit les dépôts SEC des titres cibles,
        # produit sentinelle + analyse d'entreprise, ENREGISTRE, n'affecte NI la
        # décision NI les ordres. Budget-gardée, fail-open.
        run_ai_observation(cfg, list(target.index) or list(state.holdings))

        manager = OrderManager(client, risk)
        executed = manager.execute(
            target, prices.iloc[-1], nav_history, dry_run=dry_run
        )
        if executed or dry_run:
            store.save_portfolio(decision.state)
        print(f"{len(executed)} ordres {'calculés (dry-run)' if dry_run else 'envoyés'}.")
        return 0
    finally:
        client.disconnect()


def cmd_daily(cfg: dict, dry_run: bool) -> int:
    """Job quotidien léger: NAV, plus-hauts, stops (reduce-only), breaker."""
    from hermes.data.ingestion import IBKRHistoryFetcher
    from hermes.execution.order_manager import OrderManager

    _, risk = build_params(cfg)
    store = StateStore()
    state = store.load_portfolio()
    client = _connect(cfg)
    try:
        nav = client.net_liquidation()
        held = list(state.holdings)
        closes = pd.Series(dtype=float)
        if held:
            fetcher = IBKRHistoryFetcher(client.ib)
            recent = fetcher.fetch_universe(held, duration="5 D")
            if not recent.empty:
                closes = recent.iloc[-1]

        today = pd.Timestamp.now().normalize()
        nav_history = store.append_nav(today, nav)

        decision = decide_daily(closes, nav, state, risk)
        store.save_portfolio(decision.state)

        # QW-4 : surveillance intra-mois des 8-K des positions détenues
        # (mécanique, zéro IA sur le chemin critique, aucune vente auto).
        if held:
            from hermes.intel.mechanical_flags import alert_level

            flags = fetch_mechanical_flags(cfg, held)
            alerts = alert_level(flags, held)
            for ticker, level in alerts.items():
                print(
                    f"{'🚨' if level == 'CRITICAL' else '⚠️ '} {level} 8-K sur "
                    f"position détenue {ticker} — revue humaine requise "
                    "(aucune vente automatique)."
                )

        if decision.breaker_triggered_today:
            print("🚨 COUPE-CIRCUIT déclenché — liquidation et blocage des achats.")
        if decision.stop_sales:
            print(f"Stops déclenchés (vente seule): {list(decision.stop_sales)}")
            manager = OrderManager(client, risk)
            sell_targets = pd.Series(
                0.0, index=list(decision.stop_sales), dtype=float
            )
            manager.execute(sell_targets, closes, nav_history, dry_run=dry_run)
        print(
            f"NAV {nav:,.0f} · drawdown {decision.state.drawdown:.1%} · "
            f"breaker {'ACTIF' if decision.state.breaker_active else 'inactif'}"
        )
        return 0
    finally:
        client.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(prog="hermes")
    parser.add_argument("mode", choices=["backtest", "paper", "daily"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", default="hermes/config/settings.yaml")
    args = parser.parse_args()

    cfg = load_settings(args.config)
    if args.mode == "backtest":
        return cmd_backtest(cfg)
    if args.mode == "daily":
        return cmd_daily(cfg, args.dry_run)
    return cmd_paper(cfg, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
