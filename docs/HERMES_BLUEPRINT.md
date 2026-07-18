# Blueprint Hermes — Tout ce qu'il faut pour construire un agent de trading algorithmique

> **Objectif de ce document** : t'exposer l'ensemble des briques nécessaires — outils, API, sources de données, signaux, gestion du risque, points de vigilance — pour construire un agent de trading, afin que tu puisses **comprendre et décider toi-même** à chaque étape.
>
> **Sources** : chaque affirmation renvoie soit au rapport de recherche vérifié ([`research/RAPPORT_BOURSE.md`](../research/RAPPORT_BOURSE.md), noté « **Rapport §N** »), soit au code de référence ([`hermes/`](../hermes/), qui illustre concrètement les concepts), soit est marquée « ⚠️ non vérifié par notre recherche ».
>
> **Avertissement** : document informatif, pas un conseil en investissement. Tout trading comporte un risque de perte en capital.

---

## Sommaire

1. [Vue d'ensemble : anatomie d'un agent de trading](#1-vue-densemble)
2. [Le broker et son API (la porte d'entrée vers le marché)](#2-broker--api)
3. [Les sources de données](#3-sources-de-données)
4. [Les signaux : ce qui marche vraiment selon la science](#4-signaux--indicateurs)
5. [La gestion du risque (ce qui te garde en vie)](#5-gestion-du-risque)
6. [Backtesting et validation anti-illusion](#6-backtesting--validation)
7. [La stack technique (outils concrets)](#7-stack-technique)
8. [Ce qu'il faut surveiller en production](#8-surveillance-en-production)
9. [Feuille de route et checklist](#9-feuille-de-route)

---

## 1. Vue d'ensemble

Un agent de trading algorithmique, c'est **6 composants en chaîne** :

```
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌──────────────┐   ┌────────────┐   ┌────────────┐
│ DATA FEED   │──▶│   SIGNAL    │──▶│   RISQUE    │──▶│ PORTEFEUILLE  │──▶│ EXÉCUTION   │──▶│ MONITORING  │
│ (données de │   │ (quoi       │   │ (combien,   │   │ (poids cibles │   │ (ordres au  │   │ (logs,      │
│  marché)    │   │  acheter ?) │   │  limites)   │   │  finaux)      │   │  broker)    │   │  alertes)   │
└────────────┘   └────────────┘   └────────────┘   └──────────────┘   └────────────┘   └────────────┘
```

| Composant | Rôle | Illustration dans le code |
|---|---|---|
| **Data feed** | Récupérer prix/volumes (historiques pour la recherche, temps réel pour la production) | `hermes/data/ingestion.py` |
| **Signal** | Transformer les données en décision : quels titres, dans quel sens | `hermes/strategy/momentum.py` |
| **Risque** | Dimensionner les positions, poser des limites, couper si ça tourne mal | `hermes/strategy/risk.py` |
| **Portefeuille** | Combiner signal + risque en poids cibles concrets (ex. « 22% AAPL ») | `apply_risk_overlay()` |
| **Exécution (OMS)** | Traduire les poids en ordres, les envoyer au broker, réconcilier | `hermes/execution/` |
| **Monitoring** | Journaliser chaque décision, alerter, produire des rapports | `hermes/reporting/`, logs JSONL |

**Le principe le plus important de tout ce document** : il y a **deux boucles séparées**.

- La **boucle de recherche** : données historiques → backtest → validation statistique. Elle tourne hors marché, sans risque.
- La **boucle de production** : données live → ordres réels (ou paper). Elle touche au marché.

**On ne connecte JAMAIS la boucle de production tant que la boucle de recherche n'a pas validé la stratégie** — c'est la règle qui sépare l'approche sérieuse du gambling déguisé (Rapport §1.4, §3.5 : l'essentiel des « stratégies gagnantes » en backtest sont des artefacts statistiques).

---

## 2. Broker & API

Le broker est l'intermédiaire qui exécute tes ordres. Pour un agent automatisé, il faut un broker **avec une API programmable** et — indispensable au début — un **mode paper trading** (argent fictif, marché réel).

### Comparatif (issu du Rapport §6)

| | **Interactive Brokers** | **Tradier** | **Alpaca** |
|---|---|---|---|
| **Type d'API** | TWS API (socket TCP), Web API (OAuth), FIX, Excel | REST simple | REST + WebSocket ⚠️ |
| **Marchés** | 100+ marchés mondiaux (actions, options, futures, forex, obligations) | Actions + options US | Actions US (+ crypto) ⚠️ |
| **Rate limits documentés** | 50 messages/seconde ; données historiques : max 60 requêtes/10 min, pas de doublon <15s | 60-120 requêtes/min selon endpoint, en-têtes de quota temps réel | ⚠️ non vérifié |
| **Paper trading** | Natif — ports dédiés (7497 pour TWS, 4002 pour IB Gateway) | Sandbox (60 req/min) | Réputé très simple ⚠️ |
| **Difficulté** | Élevée — la doc officielle cible des développeurs expérimentés (sockets, multithreading) | Faible | Faible ⚠️ |
| **Particularité** | Nécessite TWS ou IB Gateway **allumé en continu** sur ta machine | Pur REST, rien à installer | Pur REST ⚠️ |

⚠️ = éléments non vérifiés par notre recherche (le pipeline de vérification n'a pas produit de claims confirmées sur Alpaca — Rapport §6). À valider sur [docs.alpaca.markets](https://docs.alpaca.markets) avant de choisir.

### Ce qu'il faut regarder pour choisir

1. **Qualité du paper trading** : est-ce le même environnement API que le réel ? (IBKR : oui, mêmes API, port différent.)
2. **Rate limits** : ton bot doit les respecter sous peine de déconnexion (IBKR ferme la connexion au-delà de 50 msg/s — le code de référence se limite à 45, `hermes/execution/ibkr_client.py`).
3. **Coûts** : commissions par ordre, frais de données de marché en temps réel (souvent facturés à part).
4. **Contraintes d'infrastructure** : IBKR exige un logiciel local connecté en permanence (IB Gateway) ; les API REST pures (Tradier, Alpaca) n'exigent rien.

**Recommandation issue de la recherche** : IBKR si tu veux du sérieux multi-marchés et que la complexité ne te fait pas peur ; Tradier/Alpaca si tu veux démarrer simple sur les actions US. Le wrapper Python **`ib_insync`** masque une grande partie de la complexité IBKR.

---

## 3. Sources de données

Ton signal ne vaut que ce que valent tes données. Trois niveaux :

### Gratuit (pour démarrer et apprendre)

| Source | Contenu | Limites/conditions | Fiabilité |
|---|---|---|---|
| **SEC EDGAR** (Rapport §4, vérifié) | Tous les dépôts officiels des sociétés US : 10-K, 10-Q, 8-K, 13F + données XBRL des états financiers | API JSON gratuite **sans clé**, 10 requêtes/s max, en-tête User-Agent obligatoire (nom + email, sinon 403). Full-text search depuis 2001. Quasi temps réel (<1 min) | Maximale (source officielle du régulateur) |
| **yfinance** (Yahoo Finance) | Prix historiques ajustés, pratique en Python | Non contractuel, peut casser sans préavis — acceptable pour le backtest d'apprentissage, **pas pour la production** | Moyenne |
| **Ton broker** | IBKR fournit l'historique via son API (avec pacing strict : max 60 requêtes/10 min) | Nécessite un compte | Bonne |

### Payant retail (~10-200 €/mois) — ⚠️ non vérifié en détail par notre recherche

Polygon.io, Databento, Tiingo, EOD Historical Data, Nasdaq Data Link (ex-Quandl), Twelve Data. Notre pipeline de recherche n'a pas réussi à produire de comparatif vérifié (le contenu est trop marketing pour la vérification contradictoire — Rapport §4). **À comparer toi-même** sur : couverture (actions/options/futures), profondeur d'historique, niveaux de données (L1 = meilleures cotations, L2 = carnet d'ordres, tick = chaque transaction), latence, prix.

### Institutionnel (Bloomberg, Refinitiv/LSEG, FactSet)

~2 000+ $/mois — hors budget individuel, mentionné pour la culture générale.

### ⚠️ Les 3 pièges de données qui détruisent les backtests (Rapport §4, §8bis)

1. **Survivorship bias** : si tu backtestes sur la liste *actuelle* du S&P 500, tu exclus toutes les sociétés qui ont fait faillite ou ont été retirées — ta performance est artificiellement gonflée. Il faut des **constituants point-in-time** (la liste telle qu'elle était à chaque date). Vérifié dans le rapport : la base CRSP elle-même a eu des biais documentés (rendements surévalués, fusions mal enregistrées dans ~50% des cas — Elton, Gruber & Blake 2001).
2. **Look-ahead bias** : utiliser une donnée qui n'était pas encore connue à la date simulée (ex. : résultats trimestriels *révisés* au lieu des chiffres publiés à l'époque). Le test dans le code de référence (`tests/test_momentum.py::test_no_lookahead_score_uses_only_past_window`) montre comment vérifier ça mécaniquement.
3. **Corporate actions** : splits et dividendes non ajustés créent de faux sauts de prix. Toujours utiliser des **prix ajustés** (adjusted close).

---

## 4. Signaux & indicateurs

C'est ici que notre recherche apporte le plus de valeur : **la science a testé tout ça**, et les résultats sont contre-intuitifs.

### ✅ Ce qui a une preuve académique robuste (à privilégier)

| Signal | Preuve | Détails (Rapport §) |
|---|---|---|
| **Momentum cross-sectionnel (12-1)** | La plus robuste de toute la littérature : 30 ans de confirmations **hors-échantillon après publication** — le test ultime qu'une anomalie est réelle | Acheter les titres qui ont le plus monté sur les 12 derniers mois **en excluant le dernier mois** (à cause du reversal court terme). §1.2 |
| **Time-series momentum** | Moskowitz-Ooi-Pedersen 2012 ; persistance 1-12 mois puis renversement | Ne détenir un actif que si son propre rendement passé est positif. Fonctionne en portefeuille diversifié, pas titre par titre. §1.2 |
| **Risk-managed momentum** | Barroso & Santa-Clara 2015 : le scaling par volatilité élimine quasi les crashes du momentum et double presque le Sharpe | La version à implémenter en priorité si tu fais du momentum. §1.2 |
| **Value, quality, low-vol (facteurs)** | Confirmés sur 93 pays (Jensen-Kelly-Pedersen 2023) ; mais l'implémentabilité réelle est plus faible que les papiers (BAB : Sharpe réel ~0,49 vs 0,78 annoncé) | Horizon long (mois/années), plus adapté à l'investissement qu'au trading actif. §2 |
| **PEAD** (dérive post-annonce de résultats) | 50+ ans de réplications, 224 études | Le cours dérive dans le sens de la surprise de résultats pendant des semaines. §2.3 |

### ❌ Ce qui a une preuve faible ou réfutée (à éviter comme signal principal)

| Signal | Verdict de la recherche |
|---|---|
| **Indicateurs techniques classiques** (RSI, MACD, moyennes mobiles, Bollinger) utilisés seuls | Pouvoir prédictif historique réel mais **érodé depuis ~1990**, annulé par les coûts de transaction, et l'essentiel des « profits » en backtest vient du data-snooping (tester 1000 configs et garder la meilleure). Rapport §1.1 — c'est le résultat le plus contre-intuitif pour les débutants : les indicateurs les plus populaires sont les moins prouvés. |
| **Patterns chartistes** (têtes-épaules, triangles…) | Aucune claim vérifiée n'a pu être produite en leur faveur dans toute notre recherche. |
| **Sélection de règles sur performance passée** | Contre-productive : les règles récemment gagnantes font ensuite *moins bien* que le buy-and-hold (Rink 2023). §1.1 |
| **Transposer des signaux US vers l'Asie sans les retester** | 83% des anomalies US **échouent** sur le marché chinois (Management Science 2024). Marchés matures (Europe, Japon) : OK ; ailleurs : tout retester localement. §8 |

### 🟡 Zone grise (possible mais exigeant)

- **ML/Deep Learning** : gains réels documentés (Gu-Kelly-Xiu 2020 : les réseaux de neurones battent les modèles linéaires, Sharpe 2,35 vs 0,89) — mais échantillon pré-2016, érosion probable depuis, et risque d'overfitting démultiplié. À réserver pour plus tard. §3.3
- **Vol-timing agressif** : débat académique non tranché — gains contestés hors-échantillon et après coûts (§7). Le vol-scaling *conservateur* (inverse-vol) reste raisonnable.
- **Microstructure/order flow** : fort pouvoir explicatif court terme, mais exige une infrastructure haute fréquence hors de portée individuelle. §1.3

### La méta-leçon (la plus importante)

**Le critère qui sépare un vrai signal d'un artefact** : a-t-il survécu **hors échantillon, après publication** ? Le momentum : oui. Les règles techniques classiques : non. Et tout signal publié perd en moyenne **-58% de sa performance après publication** (McLean & Pontiff — §2.1) parce que le marché l'arbitre. Implication : ne t'attends jamais aux chiffres des papiers ; compte sur une fraction.

---

## 5. Gestion du risque

C'est le composant qui détermine ta **survie**. La recherche est claire : la plupart des traders individuels perdent non pas faute de signal, mais par excès de trading et absence de discipline.

### Position sizing (combien par position)

- **Kelly fractionnaire** (demi-Kelly typiquement) : le critère de Kelly théorique donne la taille de mise optimale pour la croissance long terme, mais calculé sur des données réelles (pas la « vraie » distribution) il est mal calibré **dans les deux sens** (Hsieh-Barmish-Gubner — §7). D'où la fraction. Ne jamais utiliser Kelly plein.
- **Pondération inverse-volatilité** : donner moins de poids aux titres les plus volatils. Simple, robuste, sans les fragilités du vol-timing agressif. Illustration : `hermes/strategy/risk.py::inverse_vol_weights`.
- **Plafond par position** (ex. 30% max) : jamais tout sur un titre.
- **Jamais de levier au départ.**

### Stops

- **Trailing stops larges** (~15%) plutôt que serrés : les stops serrés sur actions individuelles **sous-performent le buy-and-hold** à cause des coûts qu'ils génèrent (Lo & Remorov 2017 — §7).
- Les stops n'ont de valeur **qu'en régime de momentum** ; en régime de retour à la moyenne, ils font rater les rebonds (Kaminski & Lo 2014). Comme notre stratégie de référence est du momentum, ils sont cohérents ici.

### Mesures de risque du portefeuille

- **Expected Shortfall (CVaR) > VaR** : la VaR (perte maximale à 95%) échoue mathématiquement à récompenser la diversification dans les cas à queues épaisses (non-subadditivité — Artzner et al. 1999, §8bis). L'ES (perte *moyenne* dans les pires 5%) est la mesure cohérente. Surveille ton ES, pas seulement ta VaR.
- **Max drawdown** : la perte depuis le plus haut. C'est la métrique la plus parlante psychologiquement.

### Coupe-circuits (ce qui doit exister AVANT le premier ordre)

1. **Coupe-circuit de drawdown** : au-delà de X% de perte du portefeuille (ex. 15%), le bot **s'arrête tout seul**. Illustration : `hermes/strategy/risk.py::circuit_breaker_triggered`.
2. **Kill switch manuel** : un moyen trivial de tout stopper (dans le code de référence : créer un fichier `KILL_SWITCH` — aucun ordre ne part tant qu'il existe).
3. **Verrou paper/réel** : le passage en argent réel doit exiger un acte volontaire explicite, jamais un simple changement de config accidentel (illustration : double verrou dans `hermes/execution/ibkr_client.py`).
4. **Journal d'audit** : chaque décision et chaque ordre horodatés dans un fichier (JSONL) — pour comprendre *a posteriori* ce que le bot a fait et pourquoi.

### Pourquoi automatiser, au fond

La preuve comportementale (Barber & Odean 2000, §8bis) : sur 66 465 comptes réels, les 20% qui tradent le plus gagnent **11,4%/an net** contre **18,5%** pour ceux qui tradent le moins (marché : 17,9%). L'écart de ~7 points/an vient de l'**overconfidence** et du sur-trading. Un agent discipliné neutralise exactement ces biais — à condition de ne pas intervenir manuellement dans ses décisions.

---

## 6. Backtesting & validation

### Les frameworks (statuts de maintenance vérifiés au 15/07/2026 — Rapport §5)

| Framework | Points forts | Points faibles |
|---|---|---|
| **vectorbt** | Très rapide (vectorisé), activement maintenu (~8 300 étoiles, releases régulières) | Les nouvelles fonctionnalités majeures vont vers la version payante PRO |
| **zipline-reloaded** | Successeur maintenu du moteur de Quantopian, event-driven réaliste | Plus lourd à prendre en main |
| **Backtesting.py** | API très simple, bien documentée | Chiffres de popularité non confirmés |
| **bt** | Architecture élégante (arbres de stratégies) | Officiellement encore en « alpha » |
| **QuantConnect/LEAN** | Plateforme complète recherche→production, données incluses | Moteur C# (Python en surcouche) |
| **NautilusTrader** | Parité recherche/production (même code en backtest et en live), moteur Rust | Complexité élevée, changements cassants |

Un backtest maison simple et **auditable** (comme `hermes/backtest/engine.py`, ~100 lignes) est aussi une option valable pour débuter : tu comprends chaque ligne, aucun comportement caché.

### La méthodologie (non négociable)

1. **Zéro look-ahead** : le signal à la date t n'utilise que des données ≤ t. À tester mécaniquement.
2. **Coûts réalistes** : commissions + slippage (écart entre prix affiché et prix d'exécution) à chaque transaction — c'est ce qui tue la plupart des stratégies « gagnantes » (§1.1).
3. **Walk-forward** : caler les paramètres sur une période, tester sur la suivante, avancer, répéter — jamais d'optimisation sur toute la période puis « test » sur la même.

### La validation anti-illusion (l'étape que 99% des amateurs sautent)

Deux outils de López de Prado et co-auteurs (Rapport §8bis), implémentés dans `hermes/backtest/validate.py` :

- **Deflated Sharpe Ratio** : répond à « compte tenu du nombre de configurations que j'ai essayées, quelle est la probabilité que mon Sharpe soit un simple coup de chance ? ». Plus tu testes de variantes, plus le seuil monte. **Il faut compter honnêtement chaque essai** — tricher ici revient à s'auto-illusionner.
- **Probability of Backtest Overfitting (PBO)** : mesure si la config « gagnante » en échantillon reste au-dessus de la médiane hors échantillon. PBO > 30-50% = la sélection est du bruit.

**Règle absolue : pas de connexion au broker (même paper) tant que ces tests ne passent pas.**

---

## 7. Stack technique

### Librairies Python (tous statuts vérifiés — Rapport §5)

| Outil | Usage | Note |
|---|---|---|
| `pandas` / `numpy` / `scipy` | Manipulation de données, stats | Standard absolu |
| `ib_insync` | Connexion IBKR simplifiée | Le wrapper de référence pour TWS API |
| `vectorbt` | Backtests paramétriques massifs | cf. §6 |
| `quantstats` | Tearsheets HTML (Sharpe, drawdown, comparaison au benchmark) | Léger et pratique |
| `Riskfolio-Lib` | Optimisation de portefeuille avancée (26+ mesures de risque, HRP, Black-Litterman) | Pour aller plus loin que l'inverse-vol |
| `Qlib` (Microsoft) | Plateforme ML quant complète (46k étoiles) | Puissant mais « non production-ready » selon les retours, courbe d'apprentissage élevée |
| `pytest` | Tests unitaires | Obligatoire — teste le signal, le risque, les garde-fous (30 tests dans `tests/`) |

### Infrastructure

- **Une machine toujours allumée** (Raspberry Pi, mini-PC, ou VPS ~5 €/mois) pour IB Gateway + le bot. Cette session Claude Code ne peut pas héberger ça (environnement éphémère).
- **Docker** pour la portabilité (un `Dockerfile` de référence est fourni).
- **cron** pour le déclenchement périodique — une stratégie momentum mensuelle n'a besoin de tourner que quelques minutes par mois, pas 24/7.
- **Logs + alertes** : au minimum un fichier de log par ordre ; idéalement une notification (email/Telegram) à chaque rebalancing et chaque incident.

### Estimation des coûts de démarrage

| Poste | Coût |
|---|---|
| Compte paper IBKR | Gratuit |
| Données (yfinance pour apprendre) | Gratuit |
| VPS ou mini-PC | 0-10 €/mois |
| Données payantes (si besoin plus tard) | 10-200 €/mois |
| **Total pour démarrer en paper** | **~0 €** |

---

## 8. Surveillance en production

Une fois le bot en paper trading, voici ce qu'il faut suivre :

### L'écart backtest → paper → réel

- Le paper trading révèle : les remplissages partiels, les erreurs de connexion, les décalages d'horaire, les bugs de réconciliation.
- Le réel ajoute : le **slippage vrai** (ton ordre bouge le prix), les files d'attente. Attends-toi à ce que chaque étape soit **pire** que la précédente — si le paper fait déjà nettement moins bien que le backtest, c'est un signal d'alarme sur la méthodologie.

### La décroissance des signaux

- Tout signal publié s'érode (-26% hors échantillon, -58% après publication — McLean & Pontiff, §2.1). Réévalue la stratégie **chaque trimestre** : le Sharpe glissant se dégrade-t-il ? Le drawdown sort-il de l'enveloppe historique ?

### Les régimes de marché

- Le momentum a des **crashes documentés** (2009 : rebond violent des perdants — Daniel & Moskowitz, §1.2). Le vol-scaling atténue mais n'élimine pas.
- En crise, **les corrélations montent** : la diversification fond exactement quand tu en as besoin (§8bis). Ton ES/drawdown doit être calibré pour ça.

### La santé opérationnelle (checklist de monitoring)

- [ ] Connexion broker active (IB Gateway a un timeout de session quotidien — à gérer)
- [ ] Données fraîches (dernier prix < X heures)
- [ ] Positions du broker = positions attendues par le bot (réconciliation)
- [ ] Aucune erreur dans les logs depuis le dernier cycle
- [ ] Drawdown courant vs seuil du coupe-circuit

---

## 9. Feuille de route

### Phase 0 — Comprendre et décider (tu es ici)
- Lire ce blueprint ; parcourir `research/RAPPORT_BOURSE.md` pour les preuves détaillées.
- Choisir : broker (IBKR recommandé), source de données (yfinance pour apprendre), stratégie de départ (momentum 12-1 recommandé).

### Phase 1 — Recherche (hors marché, zéro risque)
- Backtester avec coûts réalistes sur 8-10 ans de données.
- Passer la validation Deflated Sharpe + PBO en comptant honnêtement les essais.
- **Critère de sortie** : verdict `approved_for_paper` ✅ — sinon, retour à la conception (et le compteur d'essais augmente).

### Phase 2 — Paper trading (marché réel, argent fictif) — **3 à 6 mois minimum**
- Compte paper IBKR + IB Gateway sur une machine dédiée.
- D'abord des **dry-runs** (ordres calculés mais non envoyés), puis les vrais cycles paper.
- Suivre l'écart paper vs backtest chaque mois.
- **Critère de sortie** : 3-6 mois de cycles sans incident technique, performance dans l'enveloppe attendue du backtest.

### Phase 3 — Bilan avant toute considération d'argent réel
- Bilan honnête : Sharpe réalisé, drawdown max, incidents, écart au backtest.
- Si et seulement si tout est cohérent → décision **séparée et explicite** sur l'argent réel, avec un capital que tu peux te permettre de perdre intégralement. Cette décision n'est pas dans le périmètre de ce document.

### Checklist de mise en route (Phase 2)

- [ ] Compte paper trading IBKR créé
- [ ] TWS ou IB Gateway installé, API activée, port paper vérifié (7497/4002)
- [ ] `pip install -r requirements.txt` + `python -m pytest tests/` → tout vert
- [ ] `python -m hermes.main backtest` → verdict ✅ (sur ta machine — Yahoo est bloqué dans l'environnement Claude)
- [ ] `python -m hermes.main paper --dry-run` → ordres cohérents dans les logs
- [ ] Premier cycle réel paper → vérifier les positions dans TWS
- [ ] cron mensuel configuré + notification de résultat
- [ ] Kill switch testé (créer le fichier `KILL_SWITCH`, vérifier qu'aucun ordre ne part, le retirer)

---

## Pour aller plus loin

- **Preuves détaillées et sources** : [`research/RAPPORT_BOURSE.md`](../research/RAPPORT_BOURSE.md) (9 cycles de recherche, ~150 claims vérifiées, tout est cité).
- **Code de référence** : [`hermes/`](../hermes/) — chaque concept de ce blueprint y est implémenté et testé (30 tests).
- **Gaps assumés de notre recherche** (à creuser toi-même si besoin) : comparatif détaillé des fournisseurs de données payants, détails Alpaca, papiers fondateurs d'exécution optimale (Almgren-Chriss, Kyle, Perold) en texte intégral, latence/colocation.
