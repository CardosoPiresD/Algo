"""Cartographie de plateau paramétrique + PBO réellement calculé — CM-2.

Protocole verrouillé (docs/HERMES_V2_ROADMAP.md) :
1. La grille est FIGÉE dans un fichier versionné AVANT les runs, jamais
   étendue après coup.
2. La config de production doit être sur un PLATEAU : le Sharpe de ses
   voisins (un pas de grille dans une seule dimension) doit dépasser 70 % du
   sien — un pic isolé est un artefact d'optimisation, pas un signal.
3. La matrice des rendements quotidiens de tous les runs alimente enfin
   `probability_of_backtest_overfitting()` — le gate PBO ≤ 0,30 devient
   réellement calculable.
4. Chaque run incrémente le registre d'essais (le n_trials gonfle et durcit
   le gate DSR — c'est voulu, c'est l'honnêteté).
"""

import itertools
import json

import pandas as pd

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.validate import sharpe_ratio
from hermes.research.trials import TrialsRegistry, data_hash
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams

# Champs de MomentumParams vs RiskParams (pour dispatcher la grille)
_MOMENTUM_FIELDS = {"lookback_months", "skip_months", "top_n", "tsmom_filter"}


def load_grid_spec(path: str) -> dict:
    """Grille figée : {param: [valeurs triées]}. Versionnée avant les runs."""
    with open(path) as f:
        spec = json.load(f)
    return {k: list(v) for k, v in spec.items()}


def expand_grid(spec: dict) -> list[dict]:
    keys = sorted(spec)
    return [dict(zip(keys, combo)) for combo in itertools.product(*(spec[k] for k in keys))]


def _build_params(overrides: dict, base_momentum: MomentumParams, base_risk: RiskParams):
    from dataclasses import replace

    m_over = {k: v for k, v in overrides.items() if k in _MOMENTUM_FIELDS}
    r_over = {k: v for k, v in overrides.items() if k not in _MOMENTUM_FIELDS}
    return replace(base_momentum, **m_over), replace(base_risk, **r_over)


def run_grid(
    prices: pd.DataFrame,
    spec: dict,
    base_momentum: MomentumParams,
    base_risk: RiskParams,
    config: BacktestConfig,
    registry: TrialsRegistry | None = None,
    risk_free_annual=0.0,
) -> pd.DataFrame:
    """Exécute toute la grille. Retourne un DataFrame indexé par config
    (une colonne par paramètre + sharpe + returns en attribut).
    """
    d_hash = data_hash(prices)
    rows = []
    returns_matrix = {}
    for i, overrides in enumerate(expand_grid(spec)):
        momentum, risk = _build_params(overrides, base_momentum, base_risk)
        result = run_backtest(prices, momentum, risk, config)
        sr = sharpe_ratio(result.returns, risk_free_annual=risk_free_annual)
        rows.append({**overrides, "sharpe": sr, "max_dd": result.max_drawdown})
        returns_matrix[i] = result.returns
        if registry is not None:
            registry.record(
                config={"grid_run": overrides},
                metrics={"sharpe": sr, "max_drawdown": result.max_drawdown},
                data_h=d_hash,
                hypothese="cartographie de plateau CM-2 (grille figée)",
            )
    df = pd.DataFrame(rows)
    df.attrs["returns_matrix"] = pd.DataFrame(returns_matrix)
    return df


def neighbors_of(overrides: dict, spec: dict) -> list[dict]:
    """Configs à UN pas de grille dans UNE seule dimension."""
    out = []
    for param, values in spec.items():
        if param not in overrides:
            continue
        idx = values.index(overrides[param])
        for step in (-1, 1):
            j = idx + step
            if 0 <= j < len(values):
                neighbor = dict(overrides)
                neighbor[param] = values[j]
                out.append(neighbor)
    return out


def plateau_check(
    grid_results: pd.DataFrame,
    spec: dict,
    prod_overrides: dict,
    threshold: float = 0.70,
) -> dict:
    """La config de production est-elle sur un plateau ?

    Critère (roadmap CM-2) : le Sharpe de CHAQUE voisin un-pas doit dépasser
    threshold × Sharpe de la config de production. Un pic isolé = rejet.
    """
    params = sorted(spec)

    def row_of(overrides):
        mask = pd.Series(True, index=grid_results.index)
        for p in params:
            mask &= grid_results[p] == overrides[p]
        matches = grid_results[mask]
        return matches.iloc[0] if len(matches) else None

    prod_row = row_of(prod_overrides)
    if prod_row is None:
        raise ValueError("Config de production absente de la grille figée")
    prod_sharpe = float(prod_row["sharpe"])

    neighbor_sharpes = []
    for n in neighbors_of(prod_overrides, spec):
        row = row_of(n)
        if row is not None:
            neighbor_sharpes.append(float(row["sharpe"]))

    if prod_sharpe <= 0:
        return {
            "prod_sharpe": prod_sharpe,
            "neighbor_sharpes": neighbor_sharpes,
            "on_plateau": False,
            "verdict": "sharpe production <= 0 — rien à valider",
        }
    floor = threshold * prod_sharpe
    weak = [s for s in neighbor_sharpes if s < floor]
    on_plateau = len(neighbor_sharpes) > 0 and not weak
    return {
        "prod_sharpe": prod_sharpe,
        "neighbor_sharpes": neighbor_sharpes,
        "floor": floor,
        "weak_neighbors": weak,
        "on_plateau": on_plateau,
        "verdict": (
            "plateau confirmé"
            if on_plateau
            else "pic isolé ou voisins faibles — rejet (artefact d'optimisation probable)"
        ),
    }
