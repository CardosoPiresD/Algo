"""CUSUM de mort du signal — CM-4. Alarme, JAMAIS actionneur.

Question : à partir de quand conclure que le momentum est mort (et pas juste
en mauvaise passe) ? Test séquentiel CUSUM (Page 1954, SPC — hors corpus,
standard) sur l'écart entre le rendement mensuel réalisé et l'ATTENTE DÉGRADÉE
(déjà décotée de −58 %, McLean & Pontiff — rapport §2.1).

Au franchissement du seuil h : statut 🟠 forcé + item obligatoire du digest +
revue humaine — le pattern existant de l'ES hors enveloppe. L'humain décide,
le bot ne touche à rien (le passage automatique à 50 % d'exposition proposé
initialement violait le design §5 couche 7 et a été retiré par le critique).

Le livrable clé est l'ANALYSE DE PUISSANCE honnête : savoir qu'il faut
plusieurs années pour détecter un signal mort est la meilleure défense contre
l'abandon émotionnel à 18 mois. Les paramètres (k, h) doivent être
PRÉ-ENREGISTRÉS avant le déploiement (state/cusum_preregistration.json).
"""

import json
import os

import numpy as np
import pandas as pd


def cusum_series(
    monthly_returns: pd.Series,
    expected_monthly: float,
    slack_k: float,
) -> pd.Series:
    """S_t = max(0, S_{t-1} + (attendu − réalisé) − k).

    S monte quand le réalisé est durablement SOUS l'attente dégradée (au-delà
    de la marge k). Une bonne passe le fait redescendre (plancher à 0).
    """
    r = monthly_returns.dropna()
    s = 0.0
    out = {}
    for date, realized in r.items():
        s = max(0.0, s + (expected_monthly - float(realized)) - slack_k)
        out[date] = s
    return pd.Series(out)


def cusum_status(
    monthly_returns: pd.Series,
    expected_monthly: float,
    slack_k: float,
    threshold_h: float,
) -> dict:
    s = cusum_series(monthly_returns, expected_monthly, slack_k)
    current = float(s.iloc[-1]) if len(s) else 0.0
    return {
        "cusum_current": current,
        "threshold_h": threshold_h,
        "alarm": current >= threshold_h,
        "action_si_alarme": (
            "statut ORANGE forcé + item obligatoire du digest + revue humaine — "
            "aucune action automatique sur le portefeuille"
        ),
        "n_months": len(s),
    }


def detection_delay_analysis(
    expected_monthly: float,
    monthly_vol: float,
    slack_k: float,
    threshold_h: float,
    n_sim: int = 2000,
    horizon_months: int = 120,
    seed: int = 42,
) -> dict:
    """Analyse de puissance : délais de détection simulés.

    Deux mondes simulés :
    - signal MORT : rendement réel = 0 (l'attente dégradée n'est plus servie) ;
    - signal VIVANT : rendement réel = attente dégradée (fausse alarme = bruit).
    Retourne les délais médians de détection et le taux de fausses alarmes,
    à écrire dans le document de pré-enregistrement AVANT le déploiement.
    """
    rng = np.random.default_rng(seed)

    def simulate(true_mean: float) -> list[int]:
        delays = []
        for _ in range(n_sim):
            s, detected = 0.0, None
            draws = rng.normal(true_mean, monthly_vol, horizon_months)
            for month, realized in enumerate(draws, start=1):
                s = max(0.0, s + (expected_monthly - realized) - slack_k)
                if s >= threshold_h:
                    detected = month
                    break
            delays.append(detected if detected is not None else horizon_months + 1)
        return delays

    dead = np.array(simulate(0.0))
    alive = np.array(simulate(expected_monthly))
    detected_dead = dead[dead <= horizon_months]
    return {
        "delai_median_signal_mort_mois": float(np.median(dead)),
        "delai_p80_signal_mort_mois": float(np.percentile(dead, 80)),
        "part_signal_mort_detecte_10ans": float((dead <= horizon_months).mean()),
        "taux_fausse_alarme_10ans": float((alive <= horizon_months).mean()),
        "note_honnete": (
            "Un signal mort met typiquement des années à être détecté avec "
            "certitude statistique — c'est structurel, pas un défaut du test. "
            "Décider plus vite = plus de fausses alarmes."
        ),
        "params": {
            "expected_monthly": expected_monthly,
            "monthly_vol": monthly_vol,
            "slack_k": slack_k,
            "threshold_h": threshold_h,
        },
    }


def write_preregistration(
    analysis: dict, path: str = "state/cusum_preregistration.json"
) -> str:
    """Fige les paramètres et l'analyse de puissance AVANT le déploiement."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(analysis, f, indent=1, default=str)
    return path
