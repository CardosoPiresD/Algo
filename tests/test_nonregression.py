"""Backtest de non-régression figé — QW-7 (docs/HERMES_V2_ROADMAP.md).

Le bug « chiffres différents mais plausibles, aucun crash » est le plus
sournois pour une personne seule. Ce test rejoue le moteur complet sur un
dataset gelé committé et compare la courbe d'equity à une référence committée.

Tolérance relative 1e-6 (documentée, roadmap QW-7) : un écart au-delà signale
un CHANGEMENT DE COMPORTEMENT à investiguer — si le changement est voulu,
régénérer la référence dans un commit dédié ne contenant QUE ce changement.
"""

import os

import numpy as np
import pandas as pd

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_frozen_backtest_matches_reference():
    prices = pd.read_csv(
        os.path.join(FIXTURES, "frozen_prices.csv"),
        parse_dates=["date"],
        index_col="date",
    )
    reference = pd.read_csv(
        os.path.join(FIXTURES, "frozen_equity_reference.csv"),
        parse_dates=["date"],
        index_col="date",
    )["equity"]

    result = run_backtest(
        prices, MomentumParams(top_n=5), RiskParams(), BacktestConfig()
    )

    assert len(result.equity_curve) == len(reference)
    np.testing.assert_allclose(
        result.equity_curve.to_numpy(),
        reference.to_numpy(),
        rtol=1e-6,
        err_msg=(
            "La courbe d'equity a dévié de la référence gelée — changement de "
            "comportement du moteur. Si c'est voulu: régénérer la référence "
            "dans un commit dédié (voir docstring)."
        ),
    )


def test_frozen_backtest_exercises_stops():
    """Le dataset gelé doit réellement exercer le chemin des stops (sinon la
    non-régression ne couvre pas le code le plus critique)."""
    prices = pd.read_csv(
        os.path.join(FIXTURES, "frozen_prices.csv"),
        parse_dates=["date"],
        index_col="date",
    )
    result = run_backtest(
        prices, MomentumParams(top_n=5), RiskParams(), BacktestConfig()
    )
    assert result.n_stop_sales > 0
