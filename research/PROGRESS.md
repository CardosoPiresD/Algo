# Suivi de la recherche — Bourse (boucle 8 cycles)

> Fichier de pilotage. Chaque cycle le lit au réveil pour connaître ce qui est **fait**, les **lacunes (gaps)** restantes, et cibler la suite. Mis à jour + committé à chaque cycle.

## Paramètres

- **Sujet** : la bourse — exhaustif (trading algo/quant **ET** investissement au sens large).
- **Portée** : marchés **US en priorité** ; Europe/Asie **uniquement sources triées sur le volet, les plus fiables**.
- **Crypto** : hors périmètre primaire (mentionnée seulement si transversale).
- **Langue** : français. Orientation **informative** (pas un conseil financier).
- **Cadence** : **~5 h entre cycles** (8 cycles, ~35-40 h au total). _(Ajustée le 2026-07-15 : le plafond d'usage de session — reset sur fenêtre glissante — a été atteint dès le cycle 2 avec un espacement de 15 min ; espacer à 5h laisse le quota se régénérer entre chaque cycle et évite les échecs de vérification/synthèse en cascade. Profondeur par cycle inchangée.)_
- **Livrable** : `research/RAPPORT_BOURSE.md` (cumulatif), commit/push à chaque cycle.

## Plan thématique des cycles

| Cycle | Thème | Statut |
|------:|-------|--------|
| 1 | Signaux techniques & microstructure | ✅ Fait (2026-07-15 ~01:40 UTC) |
| 2 | Signaux fondamentaux, macro & sentiment | ✅ Fait (2026-07-15 ~11:53-12:07 UTC, retry) |
| 3 | Stratégies quantitatives & littérature académique | ✅ Fait (2026-07-15 ~12:xx-13:xx UTC) |
| 4 | Données & flux de marché (APIs, fournisseurs) | ⚠️ Fait mais toujours incomplet après 2 tentatives (2026-07-15 ~13:xx UTC) — diagnostic structurel, voir gaps |
| 5 | Outils, frameworks & GitHub | ✅ Fait (2026-07-15 ~13:xx-14:xx UTC) |
| 6 | Exécution, brokers & infrastructure | ⚠️ Fait mais inégal (2026-07-15 ~14:xx UTC) — voir gaps |
| 7 | Gestion du risque, bonnes pratiques & pièges | ⚠️ Fait mais partiel (2026-07-15 ~15:xx UTC) — voir gaps |
| 8 | Complément gaps prioritaires (risque) | ⚠️ Fait mais très incomplet (2026-07-15 ~15:xx UTC) — 1/5 sujets couverts via pipeline |
| 8bis | Recherche manuelle (Lopez de Prado, VaR/ES, Barber & Odean, rebalancing) | ✅ Fait (2026-07-15 ~15:xx UTC) — hors pipeline adversarial |
| 9 | Sources EU/Asie + benchmarks quant | ✅ Fait (2026-07-17 ~08:xx UTC, retry après blocage nocturne) — 20 claims confirmés |
| — | **Consolidation finale & dédup** | ✅ Fait (2026-07-17) — rapport clos, 9 sections, résumé exécutif final ajouté |
| 8 | Synthèse transversale & sources fiables EU/Asie + dédup finale | ⏳ À faire |

## Lacunes / gaps identifiés (à combler par les prochains cycles)

**Reliquats du cycle 8 — COMBLÉS au cycle 8bis (recherche manuelle)** :
- [x] ~~Overfitting de backtest~~ → couvert : Deflated Sharpe Ratio (Bailey & López de Prado) + PBO/CSCV (Bailey-Borwein-López de Prado-Zhu).
- [x] ~~VaR/Expected Shortfall~~ → couvert : Artzner et al. 1999 (4 axiomes, non-subadditivité de la VaR, ES cohérente).
- [x] ~~Finance comportementale~~ → couvert : Barber & Odean 2000 (chiffres précis 11,4%/18,5%/17,9%), Shefrin & Statman 1985 (disposition effect).
- [x] ~~Rebalancing & diversification~~ → couvert : étude Vanguard (fréquence n'affecte pas le rendement), papier multi-actifs (fréquence optimale plus faible).
- **Note** : confiance légèrement inférieure au reste du rapport (recherche manuelle single-pass, pas de vérification adversariale à 3 votes) — voir `cycles/cycle-08bis-recherche-manuelle-gaps.md`. Lecture directe des PDF primaires bloquée (403) même en manuel — confirme un blocage réseau/proxy plutôt qu'un problème de méthode.

**Reliquats du cycle 7** (2/5 sous-thèmes couverts seulement — priorité haute pour cycle 8) :
- [ ] **VaR / Expected Shortfall** : limites documentées (Taleb, Basel), supériorité ES.
- [ ] **Overfitting de backtest** : Lopez de Prado (deflated Sharpe ratio, PBO), Bailey/Borwein/Zhu.
- [ ] **Biais méthodologiques** : impact chiffré survivorship bias, look-ahead bias avec exemples.
- [ ] **Finance comportementale** : Barber & Odean (overconfidence, loss aversion, disposition effect) — absent malgré centralité.
- [ ] **Rebalancing & diversification** : fréquence optimale, limites mathématiques sur actifs corrélés.

**Reliquats du cycle 6** (couverture inégale — 4/6 sous-thèmes non couverts) :
- [ ] **Alpaca** : API, rate limits, paper trading — zéro claim malgré demande explicite (contraste avec IBKR/Tradier qui ont bien fonctionné).
- [ ] **Papiers fondateurs** : Almgren-Chriss (2000/2001), Kyle (1985), Perold (1988) — seule une extension dérivée (Busseti & Lillo 2012) a été vérifiée.
- [ ] **Latence & colocation** : où ça compte réellement pour un petit trader vs le vrai HFT.
- [ ] **Architecture logicielle** : data feed, signal generation, OMS, risk management, execution.
- [ ] **Paper trading vs live trading** : écart de performance documenté.

**Reliquats du cycle 5** (outils non couverts par des claims confirmées) :
- [ ] **backtrader** — chiffres réfutés, statut réel de maintenance inconnu.
- [ ] **TA-Lib, pandas-ta, tsfresh** (analyse technique/features).
- [ ] **mlfinlab/Hudson & Thames, PyPortfolioOpt, empyrical**.
- [ ] **pandas, polars, scikit-learn, PyTorch/TensorFlow** (infra générale).
- [ ] **awesome-quant** et communautés (r/algotrading, forums Quantopian archivés).
- [ ] Comparatifs tiers indépendants (QuantStart, Hudson & Thames, Alpha Architect) — aucun n'a produit de claim confirmée ce cycle (source dominante = GitHub uniquement).

**⚠️ Reliquats MAJEURS du cycle 4/4bis** (2 tentatives, diagnostic structurel — voir note ci-dessous) :
- [ ] Fournisseurs de données de marché US : Polygon.io, Alpha Vantage, IEX Cloud, Tiingo, EOD Historical Data, Nasdaq Data Link, Twelve Data, Databento (couverture, latence, coût, niveaux L1/L2/L3/tick).
- [ ] Acteurs institutionnels : Bloomberg, Refinitiv/LSEG, FactSet.
- [x] ~~SEC EDGAR (accès gratuit, API)~~ → **couvert au cycle 4bis** (architecture, fraîcheur, full-text search, rate limits).
- [ ] Alt-data commerciaux : RavenPack, Thinknum, Quandl alt-data (offre concrète, au-delà de l'étude sociologique confirmée).
- [ ] Biais de données : survivorship bias, point-in-time vs restated data, look-ahead bias, ajustements corporate actions.
- [ ] Sources Europe/Asie : Euronext, Xetra, LSE et équivalents fiables.
- **Diagnostic (2 tentatives)** : le pipeline de vérification adversariale (conçu pour des affirmations académiques falsifiables) peine structurellement sur du contenu comparatif produit/fournisseur (pages marketing, tarifs) — cycle 4 (6 angles, brief large) et cycle 4bis (5 angles, brief resserré à 5 sujets précis) ont tous deux sous-performé, seul EDGAR (sujet factuel/officiel, pas comparatif) a bien fonctionné. **Ne pas retenter une 3e fois avec la même méthode** — envisager une recherche web directe non-adversariale pour ces sous-thèmes si on veut les combler.

**Reliquats du cycle 3** (thème 3 non couvert intégralement par des claims vérifiés) :
- [ ] **Détection de régimes** (HMM, changepoint detection) → toujours pas couvert (déjà en gap depuis cycle 1).
- [ ] **Indicateurs de volume** (OBV, VWAP, volume profile) → toujours pas couvert (déjà en gap depuis cycle 1).
- [ ] **Patterns chartistes** — étude fondatrice Lo, Mamaysky & Wang (2000) → toujours pas couvert (déjà en gap depuis cycle 1).
- [ ] **Walk-forward analysis** & cross-validation en série temporelle (purged/embargoed k-fold, López de Prado) → central pour la méthodologie de backtest, à prioriser.
- [ ] **Deflated Sharpe ratio** (Bailey & López de Prado 2014) → non couvert.

**Reliquats du cycle 2** (thème 2 non couvert intégralement par des claims vérifiés) :
- [ ] Sentiment & positionnement : Baker-Wurgler, VIX contrarian, AAII/Investors Intelligence, COT, short interest, flux de fonds → aucune claim vérifiée ce cycle.
- [ ] NLP & données alternatives : Loughran-McDonald, sentiment news/earnings calls, réseaux sociaux, satellite/carte bancaire/web scraping → aucune claim vérifiée ce cycle.
- [ ] Macro complémentaire : spreads de crédit, ISM/PMI, inflation/breakevens → non couverts.
- [ ] Géographie de la décroissance post-publication (US vs international, Jacobs & Müller) → à approfondir pour la portée EU/Asie (cycle 8).

**Reliquats du cycle 1** (thème 1 non couvert intégralement par des claims vérifiés) :
- [ ] Signaux de **volatilité** : VIX/term structure, volatility clustering, régimes de volatilité → à intégrer au cycle 3 (littérature quant) ou via un focus dédié.
- [ ] Signaux de **volume** : OBV, VWAP, volume profile → à rattraper (cycle 3 ou 6/exécution pour VWAP).
- [ ] **Bid-ask spread & price impact** au sens large (au-delà de l'OFI) → cycle 6 (exécution) est le meilleur véhicule.
- [ ] **Patterns chartistes** (têtes-épaules etc., preuve scientifique — Lo, Mamaysky & Wang 2000) → cycle 3.
- [ ] **Détection de régimes** (HMM, filtres, changepoint) → cycle 3 (ML/littérature académique).
- [ ] Re-vérifier les 4 claims « unverified » du cycle 1 (détails Brock 1992, résultats Rink 2023) → opportuniste au cycle 8.
- [ ] OFI sur marchés **US** spécifiquement (Cont-Kukanov-Stoikov 2014 à sourcer directement) → cycle 3 ou 6.

## Journal des cycles

### Cycle 9 — 2026-07-17 ~08:xx UTC — Sources EU/Asie + benchmarks quant de référence
- **Incident** : le run initial (lancé 2026-07-16 ~20:xx UTC) s'est figé pendant ~11h (agent de vérification mort sans erreur explicite, probablement plafond de session nocturne) — fichier de sortie vide, aucune notification. Détecté par inspection directe du journal du workflow (dernière activité horodatée), puis repris via `resumeFromRunId` : les 52 agents déjà réussis ont rejoué depuis le cache, le reste s'est terminé en ~29 min.
- **Volume** : 5 angles, 25 sources, 20 claims extraits, 20 vérifiés → **20 confirmés, 0 réfuté** (92/92 agents, **2,27M tokens**, 423 tool calls).
- **Ajouts principaux** : momentum européen (TSM ~0,71%/mois, Heliyon 2023 ; momentum cross-sectionnel affaibli post-2007, small caps) ; *Value and Momentum Everywhere* (Asness-Moskowitz-Pedersen 2013) couvrant explicitement Europe continentale + Japon ; **découverte clé** — 83%+ des anomalies US ne survivent PAS sur le marché A-share chinois (Li, Liu, Liu & Wei 2024, Management Science).
- **Gaps non couverts** (4/5 angles) : données officielles de bourses (Euronext, Deutsche Börse, LSE), régulateurs (ESMA/MiFID II, AMF), accès données Asie (JPX, HKEX), communautés/benchmarks (Quantpedia, SSRN, arXiv q-fin, CFA Institute) — pattern habituel (contenu comparatif/institutionnel mal servi par le pipeline adversarial).

### Consolidation finale — 2026-07-17
- Rapport maître relu intégralement, structure vérifiée (9 sections, pas de doublons de titres), sommaire mis à jour, section 9 ajoutée avec résumé exécutif final consolidant les forces/limites de l'ensemble du projet et un diagnostic méthodologique transversal (pipeline adversarial excelle sur académique/officiel, peine sur comparatif/commercial).
- **Rapport clos** — 9 cycles de recherche + 1 complément manuel, committés et poussés à chaque étape.

### Cycle 8bis — 2026-07-15 ~15:xx UTC — Recherche manuelle (hors pipeline) sur gaps restants
- **Méthode** : après échec du pipeline automatisé sur 4 sujets (2 tentatives, cycles 6/7/8), recherche manuelle directe via WebSearch/WebFetch (sans vérification adversariale à 3 votes) — décision utilisateur suite à question posée.
- **Résultat** : les 4 sujets comblés avec citations précises — Deflated Sharpe Ratio & PBO (Bailey/López de Prado/Borwein/Zhu), Artzner et al. 1999 (VaR non-subadditive, ES cohérente), Barber & Odean 2000 (chiffres exacts 11,4%/18,5%/17,9%, 66 465 foyers) + Shefrin & Statman 1985 (disposition effect), étude Vanguard sur le rebalancing + papier multi-actifs.
- **Constat méthodologique important** : la lecture directe des PDF primaires (SSRN, davidhbailey.com, Wiley, Berkeley) a échoué en 403 même en manuel — confirme que le blocage rencontré par le pipeline automatisé sur plusieurs cycles est probablement un blocage réseau/proxy général, pas une limite de la méthode de recherche automatisée en tant que telle. Les informations ont pu être reconstruites via recherche croisée (WebSearch) sur plusieurs résultats indépendants convergents.
- **Confiance** : légèrement inférieure au reste du rapport (pas de contre-vérification à 3 votes), mais citations précises et croisées.

### Cycle 8 — 2026-07-15 ~15:xx UTC — Complément gaps prioritaires (risque) ⚠️ TRÈS INCOMPLET
- **Volume** : 5 angles ciblés (López de Prado, VaR/ES, Barber & Odean, biais CRSP, rebalancing), 21 sources, 3 claims extraits, 3 vérifiés → **3 confirmés** fusionnés en 1 finding (37/37 agents, **1,19M tokens**, 224 tool calls, ~15 min).
- **Ajout** : biais chiffrés dans la base CRSP Mutual Fund (Elton, Gruber & Blake 2001) — omission bias, rendements biaisés à la hausse, mois de fusion inexacts ~50% du temps.
- **⚠️ Échec quasi total sur le brief ciblé** : 4 des 5 sujets (López de Prado, VaR/ES, Barber & Odean, rebalancing) à zéro claim — troisième cycle consécutif (après 4bis et une partie du 6) où un brief resserré sujet-par-sujet ne suffit pas à faire remonter des claims vérifiées, y compris sur des papiers académiques très célèbres (Barber & Odean). Décision : ne pas retenter avec le pipeline automatisé, ces gaps restent des limites assumées du rapport sauf recherche manuelle dédiée.
- **Total cycles ajusté** : 8→9 (cycle 9 = synthèse finale + EU/Asie, décidé après le cycle 7).

### Cycle 7 — 2026-07-15 ~15:xx UTC — Gestion du risque, bonnes pratiques & pièges ⚠️ PARTIEL
- **Volume** : 5 angles, 22 sources, 21 claims extraits, 21 vérifiés → **18 confirmés, 3 réfutés** fusionnés en 5 findings (92/92 agents, **3,22M tokens**, 794 tool calls, ~51 min, réussi en un seul passage).
- **Ajouts principaux** : volatility targeting (Moreira & Muir 2017 ; DeMiguel et al. 2024) — mais débat non tranché, contesté par Cederburg et al. (2020) et Barroso & Detzel (2021) hors échantillon/après coûts ; Kelly — contrepoint académique (Hsieh-Barmish-Gubner) montrant qu'il peut être trop conservateur, pas seulement trop agressif ; stop-loss — efficacité conditionnelle au régime (Kaminski & Lo 2014 ; Lo & Remorov 2017).
- **⚠️ Couverture partielle** : seulement 3 des 5 sous-thèmes du brief couverts (vol-scaling, Kelly, stop-loss). VaR/CVaR, overfitting de backtest (Lopez de Prado — pourtant central pour ce projet), biais look-ahead/survivorship chiffrés, finance comportementale (Barber & Odean), rebalancing/diversification : **tous à zéro claim vérifié**.
- **Gaps reportés, priorité haute pour cycle 8** : VaR/ES, Lopez de Prado (deflated Sharpe/PBO), survivorship/look-ahead bias chiffrés, Barber & Odean, rebalancing.

### Cycle 6 — 2026-07-15 ~14:xx UTC — Exécution, brokers & infrastructure ⚠️ INÉGAL
- **Volume** : 6 angles, 25 sources, 21 claims extraits, 21 vérifiés → **20 confirmés, 1 réfuté** fusionnés en 4 findings (96/96 agents, **3,11M tokens**, 664 tool calls, ~40 min, réussi en un seul passage).
- **Ajouts principaux** : API IBKR (TWS/Web/FIX/Excel, rate limits précis) ; API Tradier (rate limits par endpoint, en-têtes de quota) ; exécution optimale via Busseti & Lillo (2012) — extension du cadre Almgren-Chriss avec impact transitoire (Bouchaud et al. 2004).
- **⚠️ Couverture inégale** : Alpaca (malgré demande explicite), papiers fondateurs (Almgren-Chriss, Kyle, Perold — seule une extension a été trouvée), latence/colocation, architecture logicielle, paper vs live trading — **tous à zéro claim vérifié**. Pattern similaire au cycle 4 : bon rendement sur documentation officielle très structurée (IBKR, Tradier) et papiers académiques disponibles, mais rien sur les sujets où les sources pertinentes n'ont apparemment pas été trouvées/extraites par les angles de recherche.
- **Gaps reportés** : Alpaca, Almgren-Chriss/Kyle/Perold directs, latence, architecture OMS, paper vs live.

### Cycle 5 — 2026-07-15 ~13:xx-14:xx UTC — Outils, frameworks & bibliothèques open-source
- **Volume** : 5 angles, 21 sources, 80 claims extraits, 25 vérifiés → **19 confirmés, 6 réfutés, 0 non vérifié** (103/103 agents). Run initial échoué à la synthèse (même bug JSON schema que cycle 1) — retry quasi gratuit (36,8k tokens) grâce au cache ; run initial : **3,23M tokens**, 621 tool calls, ~42 min.
- **Ajouts principaux** : (i) backtesting — zipline-reloaded et vectorbt bien maintenus, bt en stade alpha, backtrader non confirmable ; (ii) plateformes complètes — QuantConnect/LEAN (C# + API Python) et NautilusTrader (Rust, parité recherche/prod) actifs et populaires, freqtrade confirmé GPL-3.0 avec FreqAI natif ; (iii) Qlib (Microsoft) — pipeline quant complet + agent LLM RD-Agent ; (iv) Riskfolio-Lib (optimisation portefeuille) et QuantStats (métriques performance).
- **Enseignement méthodologique** : contrairement au cycle 4 (données/fournisseurs), les statistiques GitHub (stars, commits, dates) sont des faits numériques bien vérifiables par le pipeline adversarial — 6 chiffres ont même été explicitement réfutés (mécanisme fonctionnel). Le pipeline fonctionne donc bien sur du factuel vérifiable (académique OU statistiques GitHub précises), mais mal sur du contenu marketing/comparatif qualitatif.
- **Gaps reportés** : backtrader, TA-Lib/pandas-ta/tsfresh, mlfinlab, PyPortfolioOpt, empyrical, infra générale (pandas/polars/sklearn/PyTorch), awesome-quant/communautés.

### Cycle 4bis — 2026-07-15 ~13:xx UTC — Données & flux de marché (complément ciblé, toujours partiel)
- **Volume** : 5 angles précisément ciblés (fournisseurs US, institutionnels, EDGAR, biais, EU/Asie), 24 sources, 5 claims extraits, 5 vérifiés → **4 confirmés (0 réfuté), tous unanimes** (46/46 agents, **1,4M tokens**, 266 tool calls, ~16 min).
- **Résultat** : 1 seul des 5 sujets ciblés a produit des claims (SEC EDGAR — architecture API, fraîcheur temps réel, full-text search depuis 2001, rate limits). Les 4 autres sujets (fournisseurs US, institutionnels, biais académiques, EU/Asie) : **zéro claim vérifié**, malgré un ciblage plus précis qu'au cycle 4.
- **Diagnostic** : confirmé — le pipeline de vérification adversariale ne convient pas à du contenu comparatif/marketing (fournisseurs, tarifs). Fonctionne bien seulement sur du contenu factuel officiel (EDGAR) ou académique (papiers peer-reviewed). **Décision : ne pas retenter une 3e fois avec cette méthode**, passer au cycle 5.

### Cycle 4 — 2026-07-15 ~13:xx UTC — Données & flux de marché ⚠️ INCOMPLET
- **Volume** : 6 angles, 29 sources, 8 claims extraits (rendement anormalement bas), 8 vérifiés → **6 confirmés, 2 réfutés** (61/61 agents — nettement moins que les ~103-104 des cycles précédents ; **1,9M tokens**, 371 tool calls, ~24 min).
- **Ajouts** : SimFin (données fondamentales, confiance moyenne) ; nature qualitative/sociologique de la littérature académique sur les alt-data (Hansen & Borch 2022) — ne prouve PAS statistiquement le pouvoir prédictif des alt-data.
- **⚠️ Problème identifié** : le brief demandait ~6 sous-thèmes distincts (fournisseurs US, institutionnels, EDGAR, alt-data, biais, EU/Asie) mais seulement 6 angles de recherche ont été alloués → dilution, et beaucoup de sources étaient des pages marketing produisant peu de claims falsifiables. Résultat : **quasi tout le brief reste non couvert**.
- **Décision à prendre** : lancer un cycle complémentaire ciblé sur les gaps du cycle 4 (probablement en scindant en 2 sous-cycles : fournisseurs+EDGAR d'un côté, biais de données+EU/Asie de l'autre) avant de considérer ce thème comme traité. En attendant, on continue vers le cycle 5 et on revient sur ces gaps.

### Cycle 3 — 2026-07-15 ~12:xx-13:xx UTC — Stratégies quantitatives & littérature académique
- **Volume** : 5 angles, 22 sources, 33 claims extraits, 25 vérifiés → **21 confirmés, 4 réfutés, 0 non vérifié** (104/104 agents, succès en un seul passage — **3,53M tokens**, 854 tool calls, ~58 min, sous Sonnet 5 par défaut).
- **Ajouts principaux** : (i) pairs trading (distance method) — jusqu'à 11%/an historique mais déclin structurel post-1988 (118→38 pb/mois) ; cointégration ETF récente confirme dépendance à la stabilité du spread ; (ii) market making post-Avellaneda-Stoikov — tractabilité HJB→EDO et extensions multi-actifs pour RL ; (iii) ML/DL (Gu-Kelly-Xiu 2020) — NN/arbres battent nettement le linéaire, Sharpe 2,35 vs 0,89 ; (iv) volatilité — semi-variances bonnes/mauvaises améliorent la prévision VIX ; (v) backtest — Reality Check + SPA combinés (Hsu & Kuan).
- **Note technique** : script du workflow régénéré sans le correctif de synthèse (JSON schema strict) appliqué au cycle 1 — corrigé préventivement dans le fichier, mais le run en cours a réussi sur l'ancien code avant que la correction ne s'applique (pas de nouvel échec cette fois).
- **Gaps toujours ouverts** (reportés depuis cycle 1, non comblés) : HMM/régimes, volume (OBV/VWAP), patterns chartistes (Lo-Mamaysky-Wang) — + nouveaux : walk-forward analysis, deflated Sharpe ratio.

### Cycle 2 — 2026-07-15 ~11:53-12:07 UTC — Signaux fondamentaux, macro & sentiment
- **Volume** : 5 angles, 21 sources, 83 claims extraits, 25 vérifiés → **23 confirmés, 2 réfutés, 0 non vérifié** (103/103 agents, retry après plafond de session).
- **Ajouts principaux** : (i) décroissance post-publication des anomalies (McLean & Pontiff) confirmée **spécifiquement américaine** (Jacobs & Müller — 38/39 marchés intacts) ; (ii) débat bayésien (Jensen-Kelly-Pedersen) vs fréquentiste sur la « crise de réplication » ; (iii) BAB/low-vol robuste multi-actifs mais Sharpe implémentable ~0,49 (pas 0,78) ; (iv) accruals en voie de disparition, PEAD très robuste (224 études), F-Score dépendant du régime macro ; (v) courbe des taux — historique pré-2018 solide, pas extrapolé.
- **Incident résolu** : le run initial (~01:55 UTC) avait perdu 25 votes + la synthèse sur plafond de session (`resets 11:50am UTC`) ; boucle mise en pause, cadence passée à ~5h/cycle ; retry lancé à 11:53 UTC (juste après le reset) via `resumeFromRunId` → 100 % de succès, 862k tokens sur le retry (agents déjà réussis servis depuis le cache).
- **Gaps reportés** : sentiment/positionnement, NLP/données alternatives, spreads de crédit, ISM/PMI (voir Lacunes).
- **Note** : à la demande de l'utilisateur, le **cycle 3 est lancé immédiatement** après le cycle 2 (test de consommation de tokens sous Sonnet 5, pas d'attente de 5h pour ce cycle précis) — retour à la cadence 5h ensuite si le quota le permet.

### Cycle 1 — 2026-07-15 ~01:40 UTC — Signaux techniques & microstructure
- **Volume** : 5 angles de recherche, 22 sources lues, 78 claims extraits, 25 vérifiés (3 votes contradictoires/claim) → **19 confirmés, 2 réfutés, 4 non vérifiés** (~104 agents).
- **Ajouts principaux** : (i) indicateurs techniques classiques — pouvoir prédictif historique réel (Brock-Lakonishok-LeBaron 1992) mais érodé, annulé par les coûts et le data-snooping (Park & Irwin ; Bajgrowicz & Scaillet ; Rink 2023) ; (ii) momentum cross-sectionnel et time-series = anomalie la plus robuste (Jegadeesh-Titman ; Moskowitz-Ooi-Pedersen ; survey Wiest 2023), variantes residual/risk-managed ; (iii) OFI/carnet d'ordres — fort R² explicatif court terme ; (iv) enseignements méthodo (tests hors-échantillon, Reality Check/SPA, coûts).
- **Incidents** : 1er run échoué à la synthèse (schéma JSON trop strict → corrigé en markdown libre) ; ~12 votes de vérification perdus sur limite de session (claims marqués « unverified », listés en gaps).
- **Gaps reportés** : volatilité/VIX, volume/VWAP, spread/price impact, patterns chartistes, HMM/régimes (voir section Lacunes).
