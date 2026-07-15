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
| 4 | Données & flux de marché (APIs, fournisseurs) | ⏳ À faire |
| 5 | Outils, frameworks & GitHub | ⏳ À faire |
| 6 | Exécution, brokers & infrastructure | ⏳ À faire |
| 7 | Gestion du risque, bonnes pratiques & pièges | ⏳ À faire |
| 8 | Synthèse transversale & sources fiables EU/Asie + dédup finale | ⏳ À faire |

## Lacunes / gaps identifiés (à combler par les prochains cycles)

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
