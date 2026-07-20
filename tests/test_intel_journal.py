"""Tests de la couche EDGAR mécanique (flags 8-K) et du journal de décision."""

import json

import numpy as np
import pandas as pd
import pytest

from hermes.intel.edgar_client import EdgarClient
from hermes.intel.mechanical_flags import FlagsReport, alert_level, scan_8k_flags
from hermes.ops.decision_journal import build_decision_journal, save_decision_journal
from hermes.strategy.decide import PortfolioState, decide_rebalance
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams


class FakeEdgar:
    """Double de test: métadonnées 8-K contrôlées."""

    def __init__(self, filings_by_ticker):
        self.filings_by_ticker = filings_by_ticker
        self.ciks = {t: i + 1 for i, t in enumerate(filings_by_ticker)}

    def ticker_to_cik(self):
        return dict(self.ciks)

    def recent_filings(self, cik):
        ticker = next(t for t, c in self.ciks.items() if c == cik)
        result = self.filings_by_ticker[ticker]
        if isinstance(result, Exception):
            raise result
        return result


def filing(form="8-K", date="2026-07-01", items="", accession="acc-1"):
    return {"form": form, "filingDate": date, "items": items, "accessionNumber": accession}


def test_veto_items_trigger_mechanical_veto():
    fake = FakeEdgar(
        {
            "BANKRUPT": [filing(items="1.03,9.01")],
            "RESTATED": [filing(items="4.02")],
            "CLEAN": [filing(items="2.02,9.01")],
        }
    )
    report = scan_8k_flags(
        ["BANKRUPT", "RESTATED", "CLEAN"], fake, as_of=pd.Timestamp("2026-07-15").date()
    )
    assert report.vetoed == frozenset({"BANKRUPT", "RESTATED"})
    assert "CLEAN" not in report.vetoed
    assert report.status["CLEAN"] == "analyse_ok"


def test_warn_items_do_not_veto():
    fake = FakeEdgar({"AUDIT": [filing(items="4.01")]})
    report = scan_8k_flags(["AUDIT"], fake, as_of=pd.Timestamp("2026-07-15").date())
    assert report.vetoed == frozenset()
    assert report.warnings == {"AUDIT": ["4.01"]}


def test_old_filings_outside_lookback_ignored():
    fake = FakeEdgar({"OLD": [filing(items="1.03", date="2025-01-01")]})
    report = scan_8k_flags(["OLD"], fake, as_of=pd.Timestamp("2026-07-15").date())
    assert report.vetoed == frozenset()


def test_item_matching_is_exact_not_substring():
    # "14.02" ne doit PAS matcher "4.02"
    fake = FakeEdgar({"TRICKY": [filing(items="14.02")]})
    report = scan_8k_flags(["TRICKY"], fake, as_of=pd.Timestamp("2026-07-15").date())
    assert report.vetoed == frozenset()


def test_error_state_is_distinct_from_no_data():
    fake = FakeEdgar({"BROKEN": RuntimeError("timeout")})
    report = scan_8k_flags(
        ["BROKEN", "UNKNOWN"], fake, as_of=pd.Timestamp("2026-07-15").date()
    )
    assert report.status["BROKEN"] == "erreur"
    assert report.status["UNKNOWN"] == "aucune_donnee"


def test_alert_level_only_for_held_positions():
    report = FlagsReport(
        vetoed=frozenset({"HELD_BAD", "NOT_HELD"}), warnings={"HELD_WARN": ["3.01"]}
    )
    levels = alert_level(report, held=["HELD_BAD", "HELD_WARN", "HELD_CLEAN"])
    assert levels == {"HELD_BAD": "CRITICAL", "HELD_WARN": "WARN"}


def test_edgar_client_requires_contact_in_user_agent(tmp_path):
    with pytest.raises(ValueError, match="User-Agent"):
        EdgarClient(user_agent="HermesBot", cache_dir=str(tmp_path))
    EdgarClient(user_agent="HermesBot test@example.com", cache_dir=str(tmp_path))


# ── Journal de décision ───────────────────────────────────────────────────────

def make_window(n_days=300, seed=5):
    trends = {"UP1": 0.0012, "UP2": 0.0009, "UP3": 0.0007, "DOWN": -0.001}
    dates = pd.bdate_range("2022-01-03", periods=n_days)
    rng = np.random.default_rng(seed)
    data = {
        k: 100 * np.exp(np.cumsum(rng.normal(d, 0.008, n_days)))
        for k, d in trends.items()
    }
    return pd.DataFrame(data, index=dates)


def test_journal_documents_every_ticker_and_exits(tmp_path):
    window = make_window()
    momentum, risk = MomentumParams(top_n=2), RiskParams()
    prev = PortfolioState(holdings={"DOWN": 0.1}, highs={"DOWN": 100.0}, nav=1000, nav_peak=1000)
    vetoed = frozenset({"UP2"})
    decision = decide_rebalance(window, prev, momentum, risk, vetoed=vetoed)

    journal = build_decision_journal(
        window, prev, decision, momentum, risk, vetoed=vetoed
    )
    assert set(journal["titres"]) == set(window.columns)
    assert journal["titres"]["UP2"]["veto"] is True
    assert journal["titres"]["UP2"]["poids_final"] == 0.0
    assert "DOWN" in journal["sorties"]
    assert journal["sorties"]["DOWN"] == "tsmom_negatif"
    # Cohérence poids finaux journal vs décision réelle
    for t, w in decision.target_weights.items():
        assert abs(journal["titres"][t]["poids_final"] - round(w, 6)) < 1e-9

    path = save_decision_journal(journal, state_dir=str(tmp_path))
    saved = json.load(open(path))
    assert saved["raison_cycle"] == decision.reason
