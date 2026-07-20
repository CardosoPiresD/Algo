"""Récupération du TEXTE des dépôts SEC pour lecture par l'IA.

Étend EdgarClient (métadonnées) au contenu : le document principal d'un 10-K,
10-Q ou 8-K, nettoyé du HTML, tronqué à une taille raisonnable. Ce texte est
l'ENTRÉE NON FIABLE fournie à l'IA (anti prompt-injection : traité comme des
données, jamais comme des instructions — design v2 §3.1).

Tout est gratuit (EDGAR) mais réseau : mocké dans les tests.
"""

import re
import urllib.request

ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"
INDEX_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
MAX_CHARS = 60_000  # borne la taille envoyée à l'IA (coût + pertinence)


def strip_html(html: str) -> str:
    """HTML -> texte brut lisible (suffisant pour de la lecture, pas du parsing)."""
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&#160;", " ")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
    )
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def extract_section(text: str, headings: list[str], max_chars: int = 8000) -> str | None:
    """Extrait grossièrement une section par titre (ex. 'Risk Factors').

    Recherche insensible à la casse ; renvoie du titre jusqu'à max_chars. Sert
    à ne fournir à l'IA que la partie pertinente (moins de tokens, plus ciblé).
    """
    low = text.lower()
    for h in headings:
        idx = low.find(h.lower())
        if idx != -1:
            return text[idx : idx + max_chars]
    return None


class FilingReader:
    def __init__(self, edgar_client):
        self._client = edgar_client  # EdgarClient (ou double de test)

    def _fetch_text(self, url: str) -> str:
        req = urllib.request.Request(
            url, headers={"User-Agent": self._client.user_agent}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        return strip_html(raw)[:MAX_CHARS]

    def latest_filing_text(self, cik: int, forms=("10-K", "10-Q")) -> dict | None:
        """Texte du dépôt le plus récent parmi `forms`. None si introuvable."""
        filings = self._client.recent_filings(cik)
        for f in filings:
            if f["form"] in forms:
                acc = f["accessionNumber"]
                acc_nodash = acc.replace("-", "")
                # Le document primaire est déduit via l'index du dépôt.
                doc = f.get("primaryDocument") or f"{acc}.txt"
                url = ARCHIVE_URL.format(cik=cik, acc_nodash=acc_nodash, doc=doc)
                try:
                    text = self._fetch_text(url)
                except Exception:
                    return None
                return {"form": f["form"], "accession": acc, "text": text}
        return None
