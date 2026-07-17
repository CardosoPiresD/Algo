"""Validation anti-overfitting : Deflated Sharpe Ratio et PBO (CSCV).

Base académique (voir research/RAPPORT_BOURSE.md, complément 8bis) :
- Bailey & López de Prado, "The Deflated Sharpe Ratio" (SSRN 2460551).
- Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest
  Overfitting", Journal of Computational Finance 20(4) (SSRN 2326253).

Règle Hermes : AUCUNE connexion broker tant que ces tests ne passent pas.
"""

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

EULER_GAMMA = 0.5772156649015329


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = returns.dropna()
    if len(r) < 2 or r.std() == 0:
        return 0.0
    return float(r.mean() / r.std() * np.sqrt(periods_per_year))


def expected_max_sharpe(n_trials: int, var_sharpe: float) -> float:
    """Sharpe maximal attendu sous H0 (pur bruit) après n_trials essais."""
    if n_trials <= 1:
        return 0.0
    sd = np.sqrt(var_sharpe)
    z1 = stats.norm.ppf(1 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
    return float(sd * ((1 - EULER_GAMMA) * z1 + EULER_GAMMA * z2))


def deflated_sharpe_ratio(
    returns: pd.Series,
    n_trials: int,
    var_sharpe_across_trials: float | None = None,
    periods_per_year: int = 252,
) -> float:
    """Probabilité que le Sharpe observé soit réel (pas un artefact de sélection).

    Retourne P(SR_vrai > SR0) où SR0 est le Sharpe max attendu sous pur bruit
    après n_trials essais. Interprétation: > 0.95 = très solide, < 0.5 = probable
    faux positif.
    """
    r = returns.dropna()
    t = len(r)
    if t < 10:
        return 0.0
    sr_period = float(r.mean() / r.std()) if r.std() > 0 else 0.0
    skew = float(stats.skew(r))
    kurt = float(stats.kurtosis(r, fisher=False))

    if var_sharpe_across_trials is None:
        # Approximation de la variance du Sharpe estimé sous H0 (par période)
        var_sharpe_across_trials = (1.0 / t) * (
            1 - skew * sr_period + (kurt - 1) / 4 * sr_period**2
        )
        var_sharpe_across_trials = max(var_sharpe_across_trials, 1e-12)

    sr0 = expected_max_sharpe(n_trials, var_sharpe_across_trials)
    denom = np.sqrt(
        max(1 - skew * sr_period + (kurt - 1) / 4 * sr_period**2, 1e-12)
    )
    z = (sr_period - sr0) * np.sqrt(t - 1) / denom
    return float(stats.norm.cdf(z))


def probability_of_backtest_overfitting(
    trial_returns: pd.DataFrame, n_splits: int = 8
) -> float:
    """PBO via CSCV (validation croisée symétrique combinatoire).

    trial_returns: DataFrame (index=date, colonnes=un essai/configuration).
    Découpe le temps en n_splits blocs; pour chaque combinaison de blocs
    formant l'in-sample, sélectionne la meilleure config in-sample et mesure
    son rang out-of-sample. PBO = proportion de combinaisons où la config
    choisie est sous-médiane hors échantillon.
    """
    if trial_returns.shape[1] < 2:
        return 0.0
    n_splits = min(n_splits, len(trial_returns) // 2)
    if n_splits < 2 or n_splits % 2 != 0:
        n_splits = max(2, n_splits - (n_splits % 2))

    blocks = np.array_split(np.arange(len(trial_returns)), n_splits)
    half = n_splits // 2
    below_median_count = 0
    total = 0

    for in_blocks in combinations(range(n_splits), half):
        in_idx = np.concatenate([blocks[i] for i in in_blocks])
        out_idx = np.concatenate(
            [blocks[i] for i in range(n_splits) if i not in in_blocks]
        )
        is_perf = trial_returns.iloc[in_idx].mean()
        oos_perf = trial_returns.iloc[out_idx].mean()
        best_config = is_perf.idxmax()
        oos_rank = oos_perf.rank(pct=True)[best_config]
        if oos_rank <= 0.5:
            below_median_count += 1
        total += 1

    return below_median_count / total if total else 0.0


def validate_strategy(
    returns: pd.Series,
    n_trials: int,
    min_dsr_prob: float = 0.90,
    trial_returns: pd.DataFrame | None = None,
    max_pbo: float = 0.30,
) -> dict:
    """Verdict global — la stratégie peut-elle passer en paper trading ?"""
    dsr = deflated_sharpe_ratio(returns, n_trials)
    result = {
        "sharpe": sharpe_ratio(returns),
        "deflated_sharpe_prob": dsr,
        "dsr_pass": dsr >= min_dsr_prob,
        "n_trials_declared": n_trials,
    }
    if trial_returns is not None and trial_returns.shape[1] >= 2:
        pbo = probability_of_backtest_overfitting(trial_returns)
        result["pbo"] = pbo
        result["pbo_pass"] = pbo <= max_pbo
        result["approved_for_paper"] = result["dsr_pass"] and result["pbo_pass"]
    else:
        result["pbo"] = None
        result["pbo_pass"] = None
        result["approved_for_paper"] = result["dsr_pass"]
    return result
