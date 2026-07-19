"""Tests du loader d'univers point-in-time (QW-2 — scaffold)."""

import pandas as pd
import pytest

from hermes.data.universe_pit import PITUniverseError, load_constituents, universe_at


def make_csv(tmp_path):
    path = tmp_path / "sp500_constituents.csv"
    path.write_text(
        "date,tickers\n"
        "2020-01-01,\"AAPL,MSFT,XOM\"\n"
        "2020-12-21,\"AAPL,MSFT,TSLA\"\n"  # entrée de Tesla, sortie d'XOM (exemple)
    )
    return str(path)


def test_missing_file_raises_explicit_error(tmp_path):
    with pytest.raises(PITUniverseError, match="survivorship"):
        load_constituents(str(tmp_path / "absent.csv"))


def test_universe_at_uses_latest_snapshot(tmp_path):
    cons = load_constituents(make_csv(tmp_path))
    before = universe_at("2020-06-01", cons)
    after = universe_at("2021-01-15", cons)
    assert "XOM" in before and "TSLA" not in before
    assert "TSLA" in after and "XOM" not in after


def test_universe_before_first_snapshot_raises(tmp_path):
    cons = load_constituents(make_csv(tmp_path))
    with pytest.raises(ValueError, match="Aucun snapshot"):
        universe_at("2019-01-01", cons)
