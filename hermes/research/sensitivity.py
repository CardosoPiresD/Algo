"""Sensibilité au jour de rebalancement + micro-bruit — QW-10c.

On valide la STRATÉGIE, pas un calendrier chanceux : la config passe si le
Sharpe MÉDIAN des 21 variantes décalées (J+0…J+20 après la fin de mois) reste
au-dessus du seuil. Le micro-bruit (±quelques bps sur les prix) vérifie que le
résultat ne tient pas à des ex-aequo fragiles. Diagnostic, pas sélection :
ces runs ne gonflent pas n_trials (aucune config n'est choisie sur ce critère).

(Corpus : §1.2 Gong-Liu-Liu sur l'écho de Novy-Marx ; §1.4 Rink 2023.)
"""

import numpy as np
import pandas as pd

from hermes.backtest.engine import BacktestConfig, run_backtest
from hermes.backtest.validate import sharpe_ratio
from hermes.strategy.momentum import MomentumParams, rebalance_schedule
from hermes.strategy.risk import RiskParams


def shifted_schedule(index: pd.DatetimeIndex, freq: str, offset_days: int) -> pd.DatetimeIndex:
    """Calendrier de rebalancement décalé de `offset_days` jours de bourse."""
    base = rebalance_schedule(index, freq)
    positions = index.get_indexer(base)
    shifted = [
        index[min(p + offset_days, len(index) - 1)] for p in positions if p >= 0
    ]
    return pd.DatetimeIndex(sorted(set(shifted)))


def rebalance_day_sensitivity(
    prices: pd.DataFrame,
    momentum: MomentumParams,
    risk: RiskParams,
    config: BacktestConfig,
    max_offset: int = 20,
    sharpe_threshold: float = 0.0,
    risk_free_annual=0.0,
) -> dict:
    """Sharpe pour chaque décalage J+0…J+max_offset du jour de rebalancement."""
    sharpes = {}
    for offset in range(max_offset + 1):
        schedule = shifted_schedule(prices.index, config.rebalance, offset)
        result = run_backtest(
            prices, momentum, risk, config, schedule_dates=schedule
        )
        sharpes[offset] = sharpe_ratio(result.returns, risk_free_annual=risk_free_annual)
    values = np.array(list(sharpes.values()))
    return {
        "sharpes_by_offset": sharpes,
        "median_sharpe": float(np.median(values)),
        "min_sharpe": float(values.min()),
        "max_sharpe": float(values.max()),
        "pass": float(np.median(values)) > sharpe_threshold,
    }


def price_noise_sensitivity(
    prices: pd.DataFrame,
    momentum: MomentumParams,
    risk: RiskParams,
    config: BacktestConfig,
    noise_bps: float = 10.0,
    n_draws: int = 20,
    seed: int = 42,
    risk_free_annual=0.0,
) -> dict:
    """Sharpe sous perturbation aléatoire des prix de ±noise_bps."""
    rng = np.random.default_rng(seed)
    sharpes = []
    for _ in range(n_draws):
        noise = 1 + rng.uniform(-noise_bps / 10_000, noise_bps / 10_000, prices.shape)
        noisy = prices * noise
        result = run_backtest(noisy, momentum, risk, config)
        sharpes.append(sharpe_ratio(result.returns, risk_free_annual=risk_free_annual))
    values = np.array(sharpes)
    return {
        "noise_bps": noise_bps,
        "sharpe_median": float(np.median(values)),
        "sharpe_min": float(values.min()),
        "sharpe_std": float(values.std()),
        "n_draws": n_draws,
    }
