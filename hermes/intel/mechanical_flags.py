"""Flags mécaniques 8-K — étage 0 de la sentinelle, ZÉRO IA (design v2 §3.1).

Les items critiques des 8-K sont des MÉTADONNÉES STRUCTURÉES de l'index EDGAR
(champ `items`) — aucune interprétation de texte, aucune hallucination
possible. Hiérarchie de gravité factuelle (jamais une "confidence" de LLM) :

    1.03 (faillite)                > VETO mécanique automatique
    4.02 (non-reliance états fin.) > VETO mécanique automatique
    4.01 (changement d'auditeur)   > WARN (qualification Haiku plus tard, shadow)
    3.01 (risque de delisting)     > WARN (idem)

Actif dès le jour 1 : ce module ne dépend d'aucun modèle, d'aucun budget,
d'aucun prompt. En cas d'erreur réseau EDGAR : fail-open explicite — le cycle
continue SANS flags, avec l'état `erreur` journalisé (un composant mort ne
doit jamais ressembler à « rien à signaler »).
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

VETO_ITEMS = ("1.03", "4.02")
WARN_ITEMS = ("4.01", "3.01")
LOOKBACK_DAYS = 90


@dataclass
class FlagsReport:
    vetoed: frozenset = frozenset()
    warnings: dict = field(default_factory=dict)   # ticker -> [items]
    details: dict = field(default_factory=dict)    # ticker -> [filings]
    status: dict = field(default_factory=dict)     # ticker -> analyse_ok | aucune_donnee | erreur


def _items_in(items_str: str, targets: tuple) -> list[str]:
    found = []
    for target in targets:
        for raw in str(items_str).split(","):
            if raw.strip() == target:
                found.append(target)
    return found


def scan_8k_flags(
    tickers: list[str],
    client,
    as_of: date | None = None,
    lookback_days: int = LOOKBACK_DAYS,
) -> FlagsReport:
    """Scanne les 8-K des `lookback_days` derniers jours pour chaque ticker.

    client : EdgarClient (ou double de test exposant ticker_to_cik() et
    recent_filings(cik)).
    """
    as_of = as_of or date.today()
    cutoff = (as_of - timedelta(days=lookback_days)).isoformat()

    vetoed = set()
    warnings: dict = {}
    details: dict = {}
    status: dict = {}

    try:
        cik_map = client.ticker_to_cik()
    except Exception:
        return FlagsReport(status={t: "erreur" for t in tickers})

    for ticker in tickers:
        cik = cik_map.get(ticker.upper())
        if cik is None:
            status[ticker] = "aucune_donnee"
            continue
        try:
            filings = client.recent_filings(cik)
        except Exception:
            status[ticker] = "erreur"
            continue

        hits = []
        for f in filings:
            if f["form"] not in ("8-K", "8-K/A"):
                continue
            if f["filingDate"] < cutoff:
                continue
            veto_items = _items_in(f["items"], VETO_ITEMS)
            warn_items = _items_in(f["items"], WARN_ITEMS)
            if veto_items or warn_items:
                hits.append({**f, "veto_items": veto_items, "warn_items": warn_items})
                if veto_items:
                    vetoed.add(ticker)
                if warn_items:
                    warnings.setdefault(ticker, []).extend(warn_items)
        if hits:
            details[ticker] = hits
        status[ticker] = "analyse_ok"

    return FlagsReport(
        vetoed=frozenset(vetoed),
        warnings=warnings,
        details=details,
        status=status,
    )


def alert_level(report: FlagsReport, held: list[str]) -> dict:
    """Niveau d'alerte mécanique par position détenue (QW-4).

    1.03/4.02 sur une position DÉTENUE -> CRITICAL ; 4.01/3.01 -> WARN.
    Aucune vente automatique — décision humaine ou cycle mensuel.
    """
    levels = {}
    for t in held:
        if t in report.vetoed:
            levels[t] = "CRITICAL"
        elif t in report.warnings:
            levels[t] = "WARN"
    return levels
