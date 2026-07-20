"""Client SEC EDGAR — métadonnées de dépôts (submissions API).

Contraintes vérifiées au rapport (cycle 4bis, claims 3-0 unanimes) :
- API JSON gratuite sans clé sur data.sec.gov ;
- limite de 10 requêtes/seconde par IP — throttle à 8 req/s par marge ;
- en-tête User-Agent OBLIGATOIRE (nom + email) sous peine de 403 ;
- fraîcheur quasi temps réel (<1 s après diffusion pour submissions).

Cache disque simple (TTL) pour ne pas re-télécharger à chaque check quotidien.
"""

import json
import os
import time
import urllib.request

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:0>10}.json"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


class EdgarClient:
    MIN_INTERVAL = 1.0 / 8  # 8 req/s, marge sous la limite documentée de 10

    def __init__(
        self,
        user_agent: str,
        cache_dir: str = "state/edgar_cache",
        cache_ttl_seconds: int = 6 * 3600,
    ):
        if "@" not in user_agent:
            raise ValueError(
                "User-Agent EDGAR invalide: la SEC exige un contact "
                "(ex. 'HermesBot prenom.nom@email.com') sous peine de 403."
            )
        self.user_agent = user_agent
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl_seconds
        self._last_request = 0.0
        os.makedirs(cache_dir, exist_ok=True)

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.MIN_INTERVAL:
            time.sleep(self.MIN_INTERVAL - elapsed)
        self._last_request = time.monotonic()

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    def _from_cache(self, key: str):
        path = self._cache_path(key)
        if os.path.exists(path) and time.time() - os.path.getmtime(path) < self.cache_ttl:
            with open(path) as f:
                return json.load(f)
        return None

    def _to_cache(self, key: str, data) -> None:
        with open(self._cache_path(key), "w") as f:
            json.dump(data, f)

    def _get_json(self, url: str, cache_key: str):
        cached = self._from_cache(cache_key)
        if cached is not None:
            return cached
        self._throttle()
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        self._to_cache(cache_key, data)
        return data

    def ticker_to_cik(self) -> dict[str, int]:
        """Mapping ticker -> CIK depuis le fichier officiel SEC."""
        data = self._get_json(TICKERS_URL, "company_tickers")
        return {row["ticker"].upper(): int(row["cik_str"]) for row in data.values()}

    def recent_filings(self, cik: int) -> list[dict]:
        """Dépôts récents d'une société (métadonnées structurées).

        Retourne une liste de dicts {form, filingDate, items, accessionNumber}.
        Le champ `items` des 8-K est une chaîne d'items ("4.02,9.01") — c'est
        une MÉTADONNÉE de l'index, pas du texte à interpréter.
        """
        data = self._get_json(SUBMISSIONS_URL.format(cik=cik), f"cik{cik}")
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        return [
            {
                "form": forms[i],
                "filingDate": recent.get("filingDate", [""] * len(forms))[i],
                "items": recent.get("items", [""] * len(forms))[i],
                "accessionNumber": recent.get("accessionNumber", [""] * len(forms))[i],
            }
            for i in range(len(forms))
        ]
