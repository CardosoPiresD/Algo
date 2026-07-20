"""Tests du banc de validation Phase 2 : grille/plateau, permutation,
sensibilité, chemins OOS, CUSUM."""

import numpy as np
import pandas as pd
import pytest

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.grid import (
    expand_grid,
    neighbors_of,
    plateau_check,
    run_grid,
)
from hermes.ops.cusum import cusum_series, cusum_status, detection_delay_analysis
from hermes.research.oos_paths import oos_path_distribution
from hermes.research.permutation import (
    RandomRotationSelector,
    estimate_keep_from_turnover,
    permutation_test,
)
from hermes.research.sensitivity import rebalance_day_sensitivity, shifted_schedule
from hermes.research.trials import TrialsRegistry
from hermes.strategy.momentum import MomentumParams, rebalance_schedule
from hermes.strategy.risk import RiskParams


def make_market(n_days=420, n_assets=8, seed=9):
    dates = pd.bdate_range("2021-01-04", periods=n_days)
    rng = np.random.default_rng(seed)
    data = {}
    for i in range(n_assets):
        drift = 0.0009 if i < n_assets // 2 else -0.0004
        data[f"T{i}"] = 100 * np.exp(np.cumsum(rng.normal(drift, 0.012, n_days)))
    return pd.DataFrame(data, index=dates)


CFG = BacktestConfig(initial_capital=100_000)


# ── Grille & plateau ──────────────────────────────────────────────────────────

def test_expand_grid_cartesian():
    spec = {"top_n": [3, 5], "trailing_stop_pct": [0.10, 0.15, 0.20]}
    assert len(expand_grid(spec)) == 6


def test_neighbors_one_step_one_dim():
    spec = {"top_n": [3, 5, 7], "trailing_stop_pct": [0.10, 0.15, 0.20]}
    n = neighbors_of({"top_n": 5, "trailing_stop_pct": 0.10}, spec)
    assert {"top_n": 3, "trailing_stop_pct": 0.10} in n
    assert {"top_n": 7, "trailing_stop_pct": 0.10} in n
    assert {"top_n": 5, "trailing_stop_pct": 0.15} in n
    assert len(n) == 3  # bord de grille sur trailing_stop


def test_run_grid_records_trials_and_feeds_pbo(tmp_path):
    prices = make_market()
    spec = {"top_n": [2, 3]}
    reg = TrialsRegistry(str(tmp_path / "trials.jsonl"))
    before = reg.n_trials()
    results = run_grid(
        prices, spec, MomentumParams(), RiskParams(), CFG, registry=reg
    )
    assert len(results) == 2
    assert reg.n_trials() == before + 2
    matrix = results.attrs["returns_matrix"]
    assert matrix.shape[1] == 2  # prête pour probability_of_backtest_overfitting


def test_plateau_check_detects_isolated_peak():
    spec = {"top_n": [2, 3, 4]}
    results = pd.DataFrame(
        [
            {"top_n": 2, "sharpe": 0.1, "max_dd": 0.1},
            {"top_n": 3, "sharpe": 1.5, "max_dd": 0.1},
            {"top_n": 4, "sharpe": 0.2, "max_dd": 0.1},
        ]
    )
    verdict = plateau_check(results, spec, {"top_n": 3})
    assert not verdict["on_plateau"]  # pic isolé -> rejet


def test_plateau_check_accepts_plateau():
    spec = {"top_n": [2, 3, 4]}
    results = pd.DataFrame(
        [
            {"top_n": 2, "sharpe": 0.9, "max_dd": 0.1},
            {"top_n": 3, "sharpe": 1.0, "max_dd": 0.1},
            {"top_n": 4, "sharpe": 0.85, "max_dd": 0.1},
        ]
    )
    verdict = plateau_check(results, spec, {"top_n": 3})
    assert verdict["on_plateau"]


# ── Permutation ───────────────────────────────────────────────────────────────

def test_estimate_keep_from_turnover():
    # turnover 0.4 sur top 10 -> ~2 titres remplacés -> keep 8
    assert estimate_keep_from_turnover(0.4, 10) == 8
    assert estimate_keep_from_turnover(2.0, 10) == 0
    assert estimate_keep_from_turnover(0.0, 10) == 10


def test_random_selector_respects_top_n_and_rotation():
    prices = make_market(n_days=300)
    rng = np.random.default_rng(1)
    sel = RandomRotationSelector(keep=2, rng=rng)
    w1 = sel(prices, MomentumParams(top_n=3))
    w2 = sel(prices, MomentumParams(top_n=3))
    assert len(w1) == 3 and len(w2) == 3
    assert len(set(w1.index) & set(w2.index)) >= 2  # rotation partielle


def test_permutation_test_structure():
    prices = make_market()
    out = permutation_test(
        prices, MomentumParams(top_n=3), RiskParams(), CFG, n_permutations=10
    )
    assert 0 < out["p_value"] <= 1
    assert "strategy_sharpe" in out and "keep_matched" in out


# ── Sensibilité ───────────────────────────────────────────────────────────────

def test_shifted_schedule_moves_dates_forward():
    dates = pd.bdate_range("2023-01-02", "2023-06-30")
    base = rebalance_schedule(dates, "monthly")
    shifted = shifted_schedule(dates, "monthly", 3)
    assert all(s >= b for s, b in zip(sorted(shifted)[:-1], sorted(base)[:-1]))


def test_rebalance_day_sensitivity_structure():
    prices = make_market()
    out = rebalance_day_sensitivity(
        prices, MomentumParams(top_n=3), RiskParams(), CFG, max_offset=3
    )
    assert len(out["sharpes_by_offset"]) == 4
    assert out["min_sharpe"] <= out["median_sharpe"] <= out["max_sharpe"]


# ── Chemins OOS ───────────────────────────────────────────────────────────────

def test_oos_paths_distribution():
    rng = np.random.default_rng(11)
    returns = pd.Series(
        rng.normal(0.0006, 0.01, 1000),
        index=pd.bdate_range("2020-01-01", periods=1000),
    )
    out = oos_path_distribution(returns, n_blocks=6, embargo_days=10)
    assert out["n_paths"] > 5
    assert out["sharpe_p5"] <= out["sharpe_p50"] <= out["sharpe_p95"]


def test_oos_paths_insufficient_data_raises():
    returns = pd.Series(np.zeros(50))
    with pytest.raises(ValueError):
        oos_path_distribution(returns, n_blocks=8, embargo_days=21)


# ── CUSUM ─────────────────────────────────────────────────────────────────────

def test_cusum_rises_when_signal_dead():
    dates = pd.date_range("2026-01-31", periods=24, freq="ME")
    dead = pd.Series(0.0, index=dates)  # réalise 0 vs attente 0.5%/mois
    s = cusum_series(dead, expected_monthly=0.005, slack_k=0.002)
    assert s.iloc[-1] > s.iloc[0]
    assert (s.diff().dropna() >= -1e-12).all()  # monotone ici (aucune bonne passe)


def test_cusum_stays_low_when_signal_alive():
    rng = np.random.default_rng(3)
    dates = pd.date_range("2026-01-31", periods=24, freq="ME")
    alive = pd.Series(rng.normal(0.005, 0.001, 24), index=dates)
    status = cusum_status(alive, expected_monthly=0.005, slack_k=0.002, threshold_h=0.05)
    assert not status["alarm"]


def test_cusum_never_actuates():
    status = cusum_status(
        pd.Series([-0.05] * 12), expected_monthly=0.005, slack_k=0.0, threshold_h=0.01
    )
    assert status["alarm"]
    assert "aucune action automatique" in status["action_si_alarme"]


def test_detection_delay_analysis_honest():
    out = detection_delay_analysis(
        expected_monthly=0.004,
        monthly_vol=0.04,
        slack_k=0.002,
        threshold_h=0.15,
        n_sim=200,
    )
    # Détecter un signal mort prend du temps: médiane > 12 mois avec ces params
    assert out["delai_median_signal_mort_mois"] > 12
    # Et la fausse alarme est plus rare que la vraie détection
    assert out["taux_fausse_alarme_10ans"] < out["part_signal_mort_detecte_10ans"]
