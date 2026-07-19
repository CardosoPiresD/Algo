"""État persistant du bot — design v2 §2.2.

Fichiers sous `state/` (écriture atomique tmp+rename) :
- portfolio.json    : PortfolioState sérialisé (positions, plus-hauts, breaker).
- nav_history.csv   : NAV quotidienne — prérequis du coupe-circuit (le bug v1
  « courbe d'equity à un point » est corrigé en branchant tout consommateur
  de drawdown sur cet historique).
"""

import json
import os
import tempfile
from dataclasses import asdict

import pandas as pd

from hermes.strategy.decide import PortfolioState

PORTFOLIO_FILE = "portfolio.json"
NAV_FILE = "nav_history.csv"


def _atomic_write(path: str, content: str) -> None:
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


class StateStore:
    def __init__(self, state_dir: str = "state"):
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)

    @property
    def portfolio_path(self) -> str:
        return os.path.join(self.state_dir, PORTFOLIO_FILE)

    @property
    def nav_path(self) -> str:
        return os.path.join(self.state_dir, NAV_FILE)

    def load_portfolio(self) -> PortfolioState:
        if not os.path.exists(self.portfolio_path):
            return PortfolioState()
        with open(self.portfolio_path) as f:
            data = json.load(f)
        return PortfolioState(**data)

    def save_portfolio(self, state: PortfolioState) -> None:
        _atomic_write(self.portfolio_path, json.dumps(asdict(state), indent=1))

    def load_nav_history(self) -> pd.Series:
        if not os.path.exists(self.nav_path):
            return pd.Series(dtype=float)
        df = pd.read_csv(self.nav_path, parse_dates=["date"], index_col="date")
        return df["nav"]

    def append_nav(self, date, nav: float) -> pd.Series:
        """Ajoute (ou remplace, si même date) le point NAV du jour."""
        history = self.load_nav_history()
        ts = pd.Timestamp(date).normalize()
        history.loc[ts] = float(nav)
        history = history.sort_index()
        out = history.rename("nav").to_frame()
        out.index.name = "date"
        _atomic_write(self.nav_path, out.to_csv())
        return history
