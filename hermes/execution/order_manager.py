"""Order manager : traduit les poids cibles en ordres, journalise tout.

Chaque décision et chaque ordre sont journalisés en JSONL (audit complet).
Le kill switch et le coupe-circuit de drawdown sont vérifiés AVANT tout envoi.
"""

import json
import os
from datetime import datetime, timezone

import pandas as pd

from hermes.strategy.risk import RiskParams, circuit_breaker_triggered, kill_switch_active


class OrderManager:
    def __init__(self, client, risk_params: RiskParams, log_dir: str = "logs", root: str = "."):
        self.client = client
        self.risk_params = risk_params
        self.root = root
        os.makedirs(os.path.join(root, log_dir), exist_ok=True)
        self.log_path = os.path.join(root, log_dir, "orders.jsonl")

    def _log(self, event: str, payload: dict) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **payload,
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def preflight(self, equity_curve: pd.Series) -> tuple[bool, str]:
        """Vérifications de sécurité avant tout envoi d'ordre."""
        if kill_switch_active(self.risk_params, self.root):
            self._log("blocked", {"reason": "kill_switch"})
            return False, "kill switch actif"
        if circuit_breaker_triggered(equity_curve, self.risk_params):
            self._log("blocked", {"reason": "drawdown_circuit_breaker"})
            return False, "coupe-circuit de drawdown déclenché"
        return True, "ok"

    # Quantités fractionnaires (IBKR fractional shares) : rend les poids
    # cibles atteignables sur petit capital et supprime l'artefact d'arrondi
    # int() qui polluait la réconciliation (design v2 §2.2). Les deltas dont la
    # valeur est inférieure à MIN_ORDER_VALUE sont ignorés (anti-poussière).
    MIN_ORDER_VALUE = 50.0
    QTY_DECIMALS = 4

    def compute_orders(
        self,
        target_weights: pd.Series,
        current_positions: dict[str, float],
        prices: pd.Series,
        equity: float,
    ) -> list[dict]:
        """Différence positions cibles vs actuelles -> liste d'ordres."""
        orders = []
        all_symbols = set(target_weights.index) | set(current_positions)
        for symbol in sorted(all_symbols):
            price = float(prices.get(symbol, 0))
            if price <= 0:
                continue
            target_qty = round(
                equity * float(target_weights.get(symbol, 0.0)) / price,
                self.QTY_DECIMALS,
            )
            current_qty = float(current_positions.get(symbol, 0))
            delta = round(target_qty - current_qty, self.QTY_DECIMALS)
            if abs(delta) * price < self.MIN_ORDER_VALUE:
                continue
            orders.append(
                {
                    "symbol": symbol,
                    "action": "BUY" if delta > 0 else "SELL",
                    "quantity": abs(delta),
                    "target_weight": float(target_weights.get(symbol, 0.0)),
                }
            )
        return orders

    def execute(
        self,
        target_weights: pd.Series,
        prices: pd.Series,
        equity_curve: pd.Series,
        dry_run: bool = False,
    ) -> list[dict]:
        ok, reason = self.preflight(equity_curve)
        if not ok:
            return []

        current = self.client.positions()
        equity = self.client.net_liquidation()
        orders = self.compute_orders(target_weights, current, prices, equity)
        self._log(
            "rebalance_start",
            {"n_orders": len(orders), "equity": equity, "dry_run": dry_run},
        )
        executed = []
        for order in orders:
            if dry_run:
                self._log("dry_run_order", order)
            else:
                trade = self.client.place_market_order(
                    order["symbol"], order["action"], order["quantity"]
                )
                self._log("order_sent", {**order, "order_id": trade.order.orderId})
            executed.append(order)
        self._log("rebalance_end", {"n_executed": len(executed)})
        return executed
