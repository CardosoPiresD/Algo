# Données & flux de marché — Cycle 4bis/8 (complément ciblé, toujours très partiel)

## Résumé exécutif

Ce cycle complémentaire (4bis) n'a produit des claims vérifiés que sur UN seul des cinq sujets demandés : SEC EDGAR (sujet C). Les 4 findings confirmés, tous sourcés depuis la documentation officielle SEC.gov et validés à l'unanimité (3-0), décrivent précisément l'architecture, la couverture, la fraîcheur des données et les règles d'usage des API EDGAR. En revanche, **AUCUN claim n'a survécu** pour les sujets A (fournisseurs quant US : Polygon.io, Alpha Vantage, IEX Cloud, Tiingo, EOD HD, Nasdaq Data Link, Twelve Data, Databento), B (Bloomberg/Refinitiv-LSEG/FactSet), D (biais académiques : survivorship, point-in-time, corporate actions) et E (sources Europe/Asie).

## Findings

### Architecture technique des API EDGAR — *Confiance : haute*
Hébergées sur data.sec.gov, format JSON, accès gratuit **sans authentification ni clé d'API**. Couvrent l'historique des dépôts par société et les données XBRL des états financiers (10-Q, 10-K, 8-K, 20-F, 40-F, 6-K et variantes). Source : [SEC.gov](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).

### Fraîcheur des données — *Confiance : haute*
Quasi temps réel : API submissions <1s de délai typique, API XBRL <1 min après diffusion du dépôt (délais possiblement plus longs en période de forte affluence). Source : [SEC.gov](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).

### EDGAR Full Text Search — *Confiance : haute*
Recherche en texte intégral de tous les dépôts électroniques **depuis 2001**, y compris pièces jointes et exhibits — utile pour données fondamentales/textuelles non structurées. Sources : [SEC.gov](https://www.sec.gov/edgar/search/), [FAQ](https://www.sec.gov/edgar/search/efts-faq.html).

### Contraintes d'usage programmatique — *Confiance : haute*
Limite de débit **10 requêtes/seconde par IP**, en-tête **User-Agent obligatoire** (nom + email de contact) sous peine de rejet (403 Forbidden). Sources : [SEC.gov](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data).

## Limites et réserves

Ce cycle 4bis ne couvre en profondeur QUE le sujet SEC EDGAR. Les quatre autres sujets du brief (fournisseurs quant retail US, fournisseurs institutionnels, biais académiques de données, sources Europe/Asie) n'ont produit **aucun claim ayant survécu la vérification** — soit parce que la recherche initiale n'a pas généré de claims exploitables sur ces sujets, soit parce que les claims générés n'ont pas résisté à la vérification adversariale. Même pour EDGAR, certains éléments du brief restent non traités : structure précise des formulaires 13F, détail de l'usage en recherche quant pour données point-in-time, API XBRL Frames. Toutes les sources confirmées proviennent d'une seule page primaire SEC.gov (autorité maximale mais diversité limitée).

**Diagnostic structurel** : sur deux tentatives consécutives (cycle 4 : 6/8 claims sur ~6 sous-thèmes ; cycle 4bis : 5/5 claims mais concentrées sur 1 seul des 5 sous-thèmes), le pipeline de recherche/vérification adversariale (orienté preuve académique falsifiable) peine à produire des claims vérifiables sur du contenu de type comparatif produit/fournisseur (pages marketing, tableaux de tarification, avis communautaires) — par nature moins "falsifiable" qu'un résultat de papier académique. Une troisième tentative identique a peu de chances de mieux réussir sans changer d'approche.
