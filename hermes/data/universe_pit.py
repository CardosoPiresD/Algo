"""Univers S&P 500 point-in-time — QW-2 (docs/HERMES_V2_ROADMAP.md).

Backtester sur la liste ACTUELLE du S&P 500 exclut les sociétés radiées ou
sorties de l'indice — survivorship bias qui gonfle artificiellement la
performance mesurée (rapport §4, §8bis : la base CRSP elle-même a eu des biais
documentés). Ce module charge un CSV de constituants historiques :

    data/universe/sp500_constituents.csv
    colonnes : date (YYYY-MM-DD), tickers (liste séparée par des virgules)
    une ligne = la composition de l'indice à cette date (snapshots datés).

Construction du CSV (à faire UNE fois, sur ta machine — voir roadmap QW-2) :
1. Source primaire à auditer : https://github.com/fja05680/sp500 (licence,
   méthodologie, couverture 2010-2026).
2. Validation par échantillonnage de 15-20 dates charnières (entrée de Tesla
   déc. 2020, sortie de GM 2009, faillites) contre les communiqués S&P —
   figées ensuite dans tests/test_universe_pit.py.
3. Documenter le biais résiduel : les tickers radiés n'ont souvent pas de prix
   yfinance — le backtest reste optimiste dans une mesure documentée
   (design v2 §9.1 ; le diagnostic chiffré est le chantier CM-5).
"""

import os

import pandas as pd

DEFAULT_PATH = "data/universe/sp500_constituents.csv"


class PITUniverseError(FileNotFoundError):
    pass


def load_constituents(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Charge les snapshots datés. Erreur explicite si le fichier manque."""
    if not os.path.exists(path):
        raise PITUniverseError(
            f"Fichier de constituants point-in-time introuvable: {path}\n"
            "Le backtest sur la liste actuelle du S&P 500 est survivorship-"
            "biaisé. Construire le CSV d'abord — instructions dans "
            "hermes/data/universe_pit.py (roadmap QW-2)."
        )
    df = pd.read_csv(path, parse_dates=["date"]).sort_values("date")
    if not {"date", "tickers"}.issubset(df.columns):
        raise ValueError(f"Colonnes attendues 'date,tickers' dans {path}")
    return df


def universe_at(date, constituents: pd.DataFrame) -> list[str]:
    """Composition de l'indice à la date donnée (dernier snapshot <= date)."""
    ts = pd.Timestamp(date)
    prior = constituents[constituents["date"] <= ts]
    if prior.empty:
        raise ValueError(
            f"Aucun snapshot de constituants avant {ts.date()} — "
            "étendre le CSV ou avancer la date de départ du backtest."
        )
    raw = prior.iloc[-1]["tickers"]
    return [t.strip() for t in str(raw).split(",") if t.strip()]
