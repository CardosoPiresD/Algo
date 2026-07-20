"""Test de permutation apparié en turnover — QW-10b.

La question : la config bat-elle le hasard STRUCTURÉ ? On génère N portefeuilles
aléatoires soumis aux mêmes contraintes (même univers, même top_n, même overlay
de risque, mêmes coûts) et au même turnover (rotation partielle : garder k
titres, remplacer top_n−k au hasard). p-value empirique = fraction des
portefeuilles aléatoires dont le Sharpe ≥ celui de la stratégie. Gate p < 0,10.

Complémentaire au DSR : la permutation teste la config contre le hasard
structuré, le DSR corrige la sélection parmi les essais. (Corpus : §1.4
White/Hansen ; §3.5 Hsu & Kuan ; §1.1 Brock et al.)

Réutilise le moteur réel via le hook `selector` (pas de 2e implémentation).
"""

import numpy as np
import pandas as pd

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.validate import sharpe_ratio
from hermes.strategy.momentum import MomentumParams
from hermes.strategy.risk import RiskParams


class RandomRotationSelector:
    """Sélecteur aléatoire à rotation partielle (turnover apparié).

    À chaque rebalancement : garde `keep` titres du portefeuille précédent
    (s'ils sont toujours dans l'univers), complète à top_n par tirage aléatoire
    sans remise parmi les autres titres disponibles.
    """

    def __init__(self, keep: int, rng: np.random.Generator):
        self.keep = keep
        self.rng = rng
        self._previous: list[str] = []

    def __call__(self, prices_window: pd.DataFrame, momentum: MomentumParams) -> pd.Series:
        available = [
            c for c in prices_window.columns
            if not pd.isna(prices_window.iloc[-1][c])
        ]
        held = [t for t in self._previous if t in available]
        kept = list(self.rng.choice(held, size=min(self.keep, len(held)), replace=False)) if held else []
        pool = [t for t in available if t not in kept]
        n_new = min(momentum.top_n - len(kept), len(pool))
        new = list(self.rng.choice(pool, size=n_new, replace=False)) if n_new > 0 else []
        selection = kept + new
        self._previous = selection
        if not selection:
            return pd.Series(dtype=float)
        return pd.Series(1.0 / momentum.top_n, index=selection)


def estimate_keep_from_turnover(avg_turnover: float, top_n: int) -> int:
    """Nombre de titres à conserver pour apparier le turnover observé.

    Turnover d'un rebalancement équipondéré où r titres sur top_n changent
    ≈ 2r/top_n → r ≈ turnover × top_n / 2 ; keep = top_n − r.
    """
    replaced = round(avg_turnover * top_n / 2)
    return int(np.clip(top_n - replaced, 0, top_n))


def permutation_test(
    prices: pd.DataFrame,
    momentum: MomentumParams,
    risk: RiskParams,
    config: BacktestConfig,
    n_permutations: int = 200,
    seed: int = 42,
    risk_free_annual=0.0,
) -> dict:
    """p-value empirique de la stratégie contre le hasard apparié en turnover."""
    strategy = run_backtest(prices, momentum, risk, config)
    strategy_sharpe = sharpe_ratio(strategy.returns, risk_free_annual=risk_free_annual)
    keep = estimate_keep_from_turnover(strategy.turnover, momentum.top_n)

    rng = np.random.default_rng(seed)
    random_sharpes = []
    for _ in range(n_permutations):
        selector = RandomRotationSelector(keep=keep, rng=rng)
        result = run_backtest(
            prices, momentum, risk, config, selector=selector
        )
        random_sharpes.append(
            sharpe_ratio(result.returns, risk_free_annual=risk_free_annual)
        )

    random_sharpes = np.array(random_sharpes)
    # p-value avec correction +1 (jamais exactement zéro)
    p_value = float((1 + (random_sharpes >= strategy_sharpe).sum()) / (1 + n_permutations))
    return {
        "strategy_sharpe": strategy_sharpe,
        "strategy_turnover": strategy.turnover,
        "keep_matched": keep,
        "random_sharpe_mean": float(random_sharpes.mean()),
        "random_sharpe_p95": float(np.percentile(random_sharpes, 95)),
        "p_value": p_value,
        "pass": p_value < 0.10,
        "n_permutations": n_permutations,
    }
