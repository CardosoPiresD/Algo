"""Tests des mesures de risque numpy (QW-12) et de l'enveloppe bootstrap (QW-6)."""

import numpy as np
import pandas as pd
import pytest

from hermes.backtest.envelope import (
    MCLEAN_PONTIFF_HAIRCUT,
    apply_haircut,
    bootstrap_envelope,
)
from hermes.reporting.tearsheet import (
    cdar,
    expected_shortfall,
    summary_metrics,
    ulcer_index,
)


def test_expected_shortfall_hand_computed():
    # 40 rendements: ES 97.5% = moyenne du pire 2.5% = le pire seul (1/40)
    r = pd.Series([0.01] * 39 + [-0.20])
    assert abs(expected_shortfall(r, 0.975) - 0.20) < 1e-12


def test_expected_shortfall_positive_convention():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.01, 500))
    assert expected_shortfall(r) > 0


def test_cdar_flat_curve_is_zero():
    r = pd.Series([0.001] * 100)
    assert cdar(r) == 0.0


def test_ulcer_index_increases_with_drawdown():
    calm = pd.Series([0.001] * 100)
    crash = pd.Series([0.001] * 50 + [-0.05] * 10 + [0.001] * 40)
    assert ulcer_index(crash) > ulcer_index(calm)


def test_summary_metrics_includes_v2_measures():
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0.0005, 0.01, 400))
    m = summary_metrics(r)
    assert {"es_975", "cdar_95", "ulcer_index"} <= set(m)


def test_haircut_degrades_mean_not_vol():
    rng = np.random.default_rng(3)
    r = pd.Series(rng.normal(0.001, 0.01, 1000))
    cut = apply_haircut(r)
    assert abs(cut.mean() - (1 - MCLEAN_PONTIFF_HAIRCUT) * r.mean()) < 1e-12
    assert abs(cut.std() - r.std()) < 1e-12


def test_envelope_structure_and_determinism():
    rng = np.random.default_rng(4)
    r = pd.Series(rng.normal(0.0008, 0.01, 800))
    env1 = bootstrap_envelope(r, n_boot=200, seed=7)
    env2 = bootstrap_envelope(r, n_boot=200, seed=7)
    assert env1 == env2  # déterministe à seed fixée
    for key in ("rolling_sharpe_12m_worst", "max_drawdown", "es_975"):
        assert {"p5", "p20", "p50", "p80", "p95"} <= set(env1[key])
    # Les percentiles sont ordonnés
    dd = env1["max_drawdown"]
    assert dd["p5"] <= dd["p50"] <= dd["p95"]


def test_envelope_haircut_lowers_sharpe_percentiles():
    rng = np.random.default_rng(5)
    r = pd.Series(rng.normal(0.001, 0.01, 800))
    with_cut = bootstrap_envelope(r, n_boot=200, seed=7)
    without = bootstrap_envelope(r, n_boot=200, seed=7, haircut=0.0)
    assert (
        with_cut["rolling_sharpe_12m_worst"]["p50"]
        < without["rolling_sharpe_12m_worst"]["p50"]
    )


def test_envelope_insufficient_history_raises():
    r = pd.Series(np.random.default_rng(6).normal(0, 0.01, 50))
    with pytest.raises(ValueError):
        bootstrap_envelope(r)
