"""Tests de la couche IA : garde-fous, budget, citation, shadow, fail-open.

Aucun réseau : le POST HTTP est monkeypatché. On vérifie surtout les
PROPRIÉTÉS DE SÛRETÉ — l'IA ne peut ni agir, ni halluciner une citation, ni
dépasser le budget.
"""

import json

import pytest

from hermes.ai.budget_guard import BudgetGuard
from hermes.ai.client import LLMClient, MeteredClient
from hermes.ai.schemas import citation_is_verbatim, normalize, validate_keys
from hermes.intel.company_analysis import analyze_company, save_assessments
from hermes.intel.sentinel_ai import assess_going_concern


class FakeClient:
    """Client IA déterministe pour les tests (renvoie un dict fixé)."""

    def __init__(self, data, tokens=(1000, 200), fail=False):
        self.data = data
        self.tokens = tokens
        self.fail = fail
        self.calls = 0
        self.available = True

    def complete_json(self, system, user, temperature=0.0):
        self.calls += 1
        if self.fail:
            return None

        class R:
            pass

        r = R()
        r.data = self.data
        r.prompt_tokens, r.completion_tokens = self.tokens
        r.raw = json.dumps(self.data)
        return r


# ── schémas / citation ────────────────────────────────────────────────────────

def test_citation_verbatim_accepts_real_substring():
    src = "The company has substantial doubt about its ability to continue as a going concern."
    assert citation_is_verbatim("substantial doubt about its ability", src)


def test_citation_verbatim_rejects_hallucination():
    src = "Operations were normal this quarter with no material issues."
    assert not citation_is_verbatim("substantial doubt about going concern", src)


def test_citation_rejects_too_short():
    assert not citation_is_verbatim("risk", "there is some risk here somewhere")


def test_normalize_unicode_and_spaces():
    assert normalize("  Héllo   WORLD ’x ") == normalize("héllo world 'x")


def test_validate_keys_enum():
    ok, _ = validate_keys({"verdict": "RAS"}, {"verdict": {"RAS", "GRAVE"}})
    assert ok
    bad, msg = validate_keys({"verdict": "MAYBE"}, {"verdict": {"RAS", "GRAVE"}})
    assert not bad and "énumération" in msg


# ── budget ────────────────────────────────────────────────────────────────────

def test_budget_records_and_caps(tmp_path):
    b = BudgetGuard(0.01, 1.0, 1.0, path=str(tmp_path / "spend.json"))
    assert b.can_spend("2026-07")
    # 1M in + 1M out = 2.0 € -> dépasse le plafond 0.01
    b.record("2026-07", 1_000_000, 1_000_000)
    assert not b.can_spend("2026-07")
    assert b.spent("2026-07") == pytest.approx(2.0)


def test_metered_client_stops_at_cap(tmp_path):
    fake = FakeClient({"x": 1}, tokens=(1_000_000, 0))
    b = BudgetGuard(0.5, 1.0, 1.0, path=str(tmp_path / "spend.json"))
    metered = MeteredClient(fake, b, "2026-07")
    # 1er appel: 1.0 € -> dépasse déjà 0.5, mais l'appel passe puis le budget coupe
    assert metered.complete_json("s", "u") is not None
    assert fake.calls == 1
    assert metered.complete_json("s", "u") is None  # coupé, aucun nouvel appel
    assert fake.calls == 1


def test_client_unavailable_without_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert not LLMClient().available
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    assert LLMClient().available


# ── sentinelle (shadow, veto-only, citation) ──────────────────────────────────

SOURCE = (
    "Item 4.02. There is substantial doubt about the Company's ability to "
    "continue as a going concern for the next twelve months."
)


def test_sentinel_grave_with_valid_citation():
    fake = FakeClient(
        {
            "verdict": "GRAVE",
            "categorie": "going_concern",
            "extrait_verbatim": "substantial doubt about the Company's ability to continue as a going concern",
        }
    )
    v = assess_going_concern("XYZ", SOURCE, fake)
    assert v.verdict == "GRAVE"
    assert v.citation_ok
    assert v.is_valid_grave
    assert v.applied is False  # SHADOW : jamais appliqué


def test_sentinel_grave_with_fake_citation_downgraded():
    fake = FakeClient(
        {
            "verdict": "GRAVE",
            "categorie": "going_concern",
            "extrait_verbatim": "the company will certainly go bankrupt next week",  # absent de la source
        }
    )
    v = assess_going_concern("XYZ", SOURCE, fake)
    assert not v.citation_ok
    assert v.verdict == "RAS"  # rétrogradé faute de citation vérifiable
    assert not v.is_valid_grave


def test_sentinel_no_data_and_error_states():
    fake = FakeClient({}, fail=True)
    assert assess_going_concern("XYZ", None, fake).state == "aucune_donnee"
    assert assess_going_concern("XYZ", SOURCE, fake).state == "erreur"


def test_sentinel_malformed_output_is_error():
    fake = FakeClient({"unexpected": "shape"})
    v = assess_going_concern("XYZ", SOURCE, fake)
    assert v.state == "erreur"
    assert v.verdict == "RAS"  # fail-safe


# ── analyse d'entreprise (observation seulement) ──────────────────────────────

def test_company_analysis_records_never_acts(tmp_path):
    fake = FakeClient(
        {
            "moat": 4,
            "innovation": 5,
            "management": 3,
            "intensite_concurrentielle": 4,
            "risques_cles": ["dépendance à un fournisseur", "litige en cours"],
            "resume": "Société solide avec un avantage produit.",
        }
    )
    a = analyze_company("NVDA", "some 10-K text about the business and risks", fake)
    assert a.applied is False  # jamais appliqué
    assert 1 <= a.innovation <= 5
    assert len(a.risques_cles) == 2

    path = save_assessments([a], "2026-07", state_dir=str(tmp_path))
    saved = json.load(open(path))
    assert saved["mode"] == "observation_seulement"
    assert saved["assessments"][0]["applied"] is False
    assert "AUCUN effet" in saved["avertissement"]


def test_company_analysis_clamps_scores():
    fake = FakeClient(
        {
            "moat": 9,           # hors bornes -> clampé à 5
            "innovation": 0,     # -> 1
            "management": "n/a", # -> 3
            "intensite_concurrentielle": 3,
            "risques_cles": "un seul risque en string",
            "resume": "x",
        }
    )
    a = analyze_company("T", "text", fake)
    assert a.moat == 5 and a.innovation == 1 and a.management == 3
    assert isinstance(a.risques_cles, list)


def test_company_analysis_no_data():
    fake = FakeClient({})
    assert analyze_company("T", None, fake).state == "aucune_donnee"
