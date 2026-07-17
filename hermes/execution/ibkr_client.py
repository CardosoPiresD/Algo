"""Client IBKR (ib_insync) — paper trading avec triple garde-fou.

Garde-fous:
1. Refus de se connecter si account_type != "paper" sans le fichier
   HERMES_LIVE_ACKNOWLEDGED (verrou anti-passage-en-réel accidentel).
2. Vérification du port: 7497/4002 sont les ports paper par défaut; un port
   live (7496/4001) avec account_type=paper est rejeté.
3. Throttling à max_messages_per_second (limite documentée IBKR: 50 msg/s,
   marge appliquée).
"""

import os
import time


PAPER_PORTS = {7497, 4002}
LIVE_ACK_FILE = "HERMES_LIVE_ACKNOWLEDGED"


class SafetyError(RuntimeError):
    pass


class IBKRClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,
        client_id: int = 42,
        account_type: str = "paper",
        max_messages_per_second: float = 45.0,
        root: str = ".",
    ):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.account_type = account_type
        self._min_interval = 1.0 / max_messages_per_second
        self._last_send = 0.0
        self._root = root
        self._ib = None
        self._check_safety()

    def _check_safety(self) -> None:
        if self.account_type != "paper":
            if not os.path.exists(os.path.join(self._root, LIVE_ACK_FILE)):
                raise SafetyError(
                    "account_type != paper mais le fichier HERMES_LIVE_ACKNOWLEDGED "
                    "est absent. Hermes est configuré paper-only par décision "
                    "explicite — voir README."
                )
        elif self.port not in PAPER_PORTS:
            raise SafetyError(
                f"account_type=paper mais port={self.port} n'est pas un port paper "
                f"connu ({sorted(PAPER_PORTS)}). Vérifier la configuration TWS/Gateway."
            )

    def connect(self):
        from ib_insync import IB

        self._ib = IB()
        self._ib.connect(self.host, self.port, clientId=self.client_id)
        return self._ib

    def disconnect(self) -> None:
        if self._ib is not None and self._ib.isConnected():
            self._ib.disconnect()

    @property
    def ib(self):
        if self._ib is None or not self._ib.isConnected():
            raise RuntimeError("Non connecté — appeler connect() d'abord.")
        return self._ib

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_send
        wait = self._min_interval - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_send = time.monotonic()

    def place_market_order(self, symbol: str, action: str, quantity: int):
        from ib_insync import MarketOrder, Stock

        if quantity <= 0:
            raise ValueError("quantity doit être > 0")
        if action not in {"BUY", "SELL"}:
            raise ValueError("action doit être BUY ou SELL")
        self._throttle()
        contract = Stock(symbol, "SMART", "USD")
        order = MarketOrder(action, quantity)
        trade = self.ib.placeOrder(contract, order)
        return trade

    def positions(self) -> dict[str, float]:
        self._throttle()
        return {
            p.contract.symbol: p.position
            for p in self.ib.positions()
            if p.contract.secType == "STK"
        }

    def net_liquidation(self) -> float:
        self._throttle()
        for row in self.ib.accountSummary():
            if row.tag == "NetLiquidation":
                return float(row.value)
        raise RuntimeError("NetLiquidation introuvable dans accountSummary")
