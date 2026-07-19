"""Tests de l'état persistant (ops/state.py) et du registre d'essais (QW-8)."""

import numpy as np
import pandas as pd

from hermes.ops.state import StateStore
from hermes.research.trials import (
    HISTORICAL_TRIALS_BASELINE,
    TrialsRegistry,
    config_hash,
    data_hash,
)
from hermes.strategy.decide import PortfolioState


def test_state_roundtrip(tmp_path):
    store = StateStore(str(tmp_path / "state"))
    state = PortfolioState(
        holdings={"AAPL": 0.12},
        highs={"AAPL": 234.5},
        nav=105_000.0,
        nav_peak=110_000.0,
        breaker_active=True,
        reentry_scale=0.5,
    )
    store.save_portfolio(state)
    loaded = store.load_portfolio()
    assert loaded == state


def test_state_default_when_missing(tmp_path):
    store = StateStore(str(tmp_path / "state"))
    assert store.load_portfolio() == PortfolioState()


def test_nav_history_append_and_idempotent(tmp_path):
    store = StateStore(str(tmp_path / "state"))
    store.append_nav("2026-07-01", 100_000)
    store.append_nav("2026-07-02", 101_000)
    # Ré-exécution du même jour: remplace, pas de doublon
    history = store.append_nav("2026-07-02", 101_500)
    assert len(history) == 2
    assert history.iloc[-1] == 101_500


def test_registry_counts_distinct_trials(tmp_path):
    reg = TrialsRegistry(str(tmp_path / "trials.jsonl"))
    assert reg.n_trials() == HISTORICAL_TRIALS_BASELINE
    cfg_a = {"top_n": 10}
    reg.record(cfg_a, {"sharpe": 0.8}, data_h="d1")
    reg.record(cfg_a, {"sharpe": 0.8}, data_h="d1")  # même config+données: 1 seul
    assert reg.n_trials() == HISTORICAL_TRIALS_BASELINE + 1
    reg.record(cfg_a, {"sharpe": 0.7}, data_h="d2")  # données rafraîchies: +1
    reg.record({"top_n": 5}, {"sharpe": 1.1}, data_h="d1")  # config nouvelle: +1
    assert reg.n_trials() == HISTORICAL_TRIALS_BASELINE + 3


def test_registry_empirical_variance_needs_three(tmp_path):
    reg = TrialsRegistry(str(tmp_path / "trials.jsonl"))
    reg.record({"a": 1}, {"sharpe": 0.5}, data_h="d1")
    reg.record({"a": 2}, {"sharpe": 0.9}, data_h="d1")
    assert reg.sharpe_variance() is None
    reg.record({"a": 3}, {"sharpe": 0.7}, data_h="d1")
    var = reg.sharpe_variance()
    assert var is not None
    assert abs(var - np.var([0.5, 0.9, 0.7], ddof=1)) < 1e-12


def test_registry_exploratory_status(tmp_path):
    reg = TrialsRegistry(str(tmp_path / "trials.jsonl"))
    e1 = reg.record({"a": 1}, {"sharpe": 0.5}, data_h="d1")
    e2 = reg.record({"a": 2}, {"sharpe": 0.6}, data_h="d1", hypothese="lookback plus court")
    assert e1["statut"] == "exploratoire"
    assert e2["statut"] == "hypothese"


def test_config_hash_stable_and_data_hash_sensitive():
    assert config_hash({"b": 2, "a": 1}) == config_hash({"a": 1, "b": 2})
    dates = pd.bdate_range("2024-01-01", periods=50)
    p1 = pd.DataFrame({"A": np.linspace(100, 110, 50)}, index=dates)
    p2 = p1.copy()
    p2.iloc[10, 0] += 0.01  # révision silencieuse type yfinance
    assert data_hash(p1) != data_hash(p2)
