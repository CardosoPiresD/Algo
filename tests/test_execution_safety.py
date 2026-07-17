import pandas as pd
import pytest

from hermes.execution.ibkr_client import IBKRClient, SafetyError
from hermes.execution.order_manager import OrderManager
from hermes.strategy.risk import RiskParams


def test_live_without_ack_file_rejected(tmp_path):
    with pytest.raises(SafetyError):
        IBKRClient(account_type="live", root=str(tmp_path))


def test_live_with_ack_file_accepted(tmp_path):
    (tmp_path / "HERMES_LIVE_ACKNOWLEDGED").touch()
    IBKRClient(account_type="live", port=7496, root=str(tmp_path))


def test_paper_on_live_port_rejected(tmp_path):
    with pytest.raises(SafetyError):
        IBKRClient(account_type="paper", port=7496, root=str(tmp_path))


def test_paper_on_paper_port_ok(tmp_path):
    IBKRClient(account_type="paper", port=7497, root=str(tmp_path))
    IBKRClient(account_type="paper", port=4002, root=str(tmp_path))


class FakeClient:
    def __init__(self):
        self.orders = []

    def positions(self):
        return {"AAPL": 10}

    def net_liquidation(self):
        return 100_000.0

    def place_market_order(self, symbol, action, quantity):
        self.orders.append((symbol, action, quantity))

        class T:
            class order:
                orderId = len(self.orders)

        return T()


def test_order_manager_kill_switch_blocks_all(tmp_path):
    (tmp_path / "KILL_SWITCH").touch()
    manager = OrderManager(FakeClient(), RiskParams(), root=str(tmp_path))
    target = pd.Series({"MSFT": 0.5})
    prices = pd.Series({"MSFT": 400.0, "AAPL": 200.0})
    executed = manager.execute(target, prices, pd.Series([100_000.0]))
    assert executed == []


def test_order_manager_circuit_breaker_blocks(tmp_path):
    manager = OrderManager(
        FakeClient(), RiskParams(max_drawdown_circuit_breaker=0.10), root=str(tmp_path)
    )
    crashed = pd.Series([100_000.0, 110_000.0, 85_000.0])
    executed = manager.execute(
        pd.Series({"MSFT": 0.5}), pd.Series({"MSFT": 400.0}), crashed
    )
    assert executed == []


def test_order_manager_computes_delta_orders(tmp_path):
    client = FakeClient()
    manager = OrderManager(client, RiskParams(), root=str(tmp_path))
    target = pd.Series({"MSFT": 0.4})
    prices = pd.Series({"MSFT": 400.0, "AAPL": 200.0})
    executed = manager.execute(target, prices, pd.Series([100_000.0]), dry_run=True)
    symbols = {o["symbol"]: o for o in executed}
    assert symbols["MSFT"]["action"] == "BUY"
    assert symbols["MSFT"]["quantity"] == 100
    assert symbols["AAPL"]["action"] == "SELL"
    assert symbols["AAPL"]["quantity"] == 10
    assert client.orders == []  # dry_run: rien envoyé


def test_order_manager_logs_audit_trail(tmp_path):
    manager = OrderManager(FakeClient(), RiskParams(), root=str(tmp_path))
    manager.execute(
        pd.Series({"MSFT": 0.4}),
        pd.Series({"MSFT": 400.0, "AAPL": 200.0}),
        pd.Series([100_000.0]),
        dry_run=True,
    )
    log = (tmp_path / "logs" / "orders.jsonl").read_text()
    assert "rebalance_start" in log
    assert "dry_run_order" in log
    assert "rebalance_end" in log
