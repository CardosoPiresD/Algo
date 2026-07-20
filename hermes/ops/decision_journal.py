"""Journal de décision 100 % mécanique — QW-5 (docs/HERMES_V2_ROADMAP.md).

À chaque rebalancement, persiste dans state/decisions/YYYY-MM.json le POURQUOI
de chaque position : score momentum 12-1, rang, filtre TSMOM, veto, poids brut
inverse-vol, poids final après vol-target/caps ; et pour les sortants, la cause
exacte. Les valeurs intermédiaires ne sont plus calculées puis jetées — elles
servent la confiance de l'opérateur, l'audit des vetos et le debugging de la
réconciliation. Aucun appel IA ici : la narration (Haiku) viendra plus tard,
lira ce fichier, et tous ses chiffres en proviendront.
"""

import json
import os

import pandas as pd

from hermes.strategy.decide import PortfolioState, RebalanceDecision
from hermes.strategy.momentum import MomentumParams, momentum_score
from hermes.strategy.risk import RiskParams, inverse_vol_weights


def build_decision_journal(
    prices_window: pd.DataFrame,
    previous_state: PortfolioState,
    decision: RebalanceDecision,
    momentum: MomentumParams,
    risk: RiskParams,
    vetoed: frozenset = frozenset(),
    stop_sales_since_last: tuple = (),
) -> dict:
    """Reconstruit mécaniquement chaque étape de la décision (fonctions pures,
    mêmes entrées que decide_rebalance → mêmes valeurs)."""
    scores = momentum_score(prices_window, momentum).dropna().sort_values(ascending=False)
    ranks = {t: i + 1 for i, t in enumerate(scores.index)}

    selected_pre_veto = scores[scores > 0].nlargest(momentum.top_n) if momentum.tsmom_filter else scores.nlargest(momentum.top_n)
    kept = [t for t in selected_pre_veto.index if t not in vetoed]
    raw_weights = inverse_vol_weights(
        prices_window, pd.Series(1.0 / momentum.top_n, index=kept), risk
    ) if kept else pd.Series(dtype=float)

    per_ticker = {}
    for t in prices_window.columns:
        score = scores.get(t)
        entry = {
            "momentum_12_1": None if score is None or pd.isna(score) else round(float(score), 6),
            "rang": ranks.get(t),
            "tsmom_ok": bool(score is not None and not pd.isna(score) and score > 0),
            "veto": t in vetoed,
            "poids_brut_inverse_vol": round(float(raw_weights.get(t, 0.0)), 6),
            "poids_final": round(float(decision.target_weights.get(t, 0.0)), 6),
        }
        per_ticker[t] = entry

    exits = {}
    for t in previous_state.holdings:
        if t in decision.target_weights:
            continue
        if t in stop_sales_since_last:
            cause = "trailing_stop"
        elif t in vetoed:
            cause = "veto_flag_8k"
        elif t in scores and scores[t] <= 0:
            cause = "tsmom_negatif"
        elif ranks.get(t, 10**9) > momentum.top_n:
            cause = f"rang_momentum_{ranks.get(t)}_hors_top_{momentum.top_n}"
        else:
            cause = "non_retenu"
        exits[t] = cause

    return {
        "date": str(prices_window.index[-1].date()),
        "raison_cycle": decision.reason,
        "exposition_totale": round(float(sum(decision.target_weights.values())), 6),
        "drawdown_courant": round(previous_state.drawdown, 6),
        "titres": per_ticker,
        "sorties": exits,
        "vetos_appliques": sorted(vetoed),
    }


def save_decision_journal(
    journal: dict, state_dir: str = "state"
) -> str:
    month = journal["date"][:7]
    directory = os.path.join(state_dir, "decisions")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{month}.json")
    with open(path, "w") as f:
        json.dump(journal, f, indent=1, ensure_ascii=False)
    return path
