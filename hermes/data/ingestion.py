"""Ingestion de données : yfinance pour le backtest, IBKR pour le live.

Rate limits IBKR documentés (rapport §6) : pas de requêtes historiques
identiques à <15s d'intervalle, max 6 requêtes/contrat/2s, max 60/10min —
d'où le throttling intégré côté IBKR.
"""

import time

import pandas as pd


def fetch_history_yfinance(
    tickers: list[str], start: str, end: str | None = None
) -> pd.DataFrame:
    """Prix de clôture ajustés quotidiens via yfinance (backtest uniquement)."""
    import yfinance as yf

    data = yf.download(
        tickers, start=start, end=end, auto_adjust=True, progress=False
    )
    closes = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]
    if isinstance(closes, pd.Series):
        closes = closes.to_frame(tickers[0])
    return closes.dropna(how="all")


class IBKRHistoryFetcher:
    """Récupération d'historique via IBKR avec pacing conforme aux limites."""

    MIN_SECONDS_BETWEEN_REQUESTS = 11.0  # 60 requêtes / 10 min => 1 / 10s + marge

    def __init__(self, ib):
        self._ib = ib
        self._last_request_ts = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_ts
        wait = self.MIN_SECONDS_BETWEEN_REQUESTS - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_ts = time.monotonic()

    def fetch_daily(self, symbol: str, duration: str = "2 Y") -> pd.DataFrame:
        from ib_insync import Stock, util

        self._throttle()
        contract = Stock(symbol, "SMART", "USD")
        bars = self._ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting="1 day",
            whatToShow="ADJUSTED_LAST",
            useRTH=True,
        )
        df = util.df(bars)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.set_index("date")[["close"]].rename(columns={"close": symbol})
        df.index = pd.to_datetime(df.index)
        return df

    def fetch_universe(self, symbols: list[str], duration: str = "2 Y") -> pd.DataFrame:
        frames = [self.fetch_daily(s, duration) for s in symbols]
        frames = [f for f in frames if not f.empty]
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, axis=1).sort_index()
