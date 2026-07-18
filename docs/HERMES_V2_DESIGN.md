# HERMES v2 « SENTINELLE » — Synthèse finale de l'architecte en chef

*Fusion des 5 designs (quant-rigoureux, ia-maximaliste, risque-sécurité, simplicité-pragmatique, production-ops) corrigée des failles convergentes identifiées par les 10 critiques adversariales. Vérifié contre le code réel du repo (`hermes/`), le rapport `research/RAPPORT_BOURSE.md` et le blueprint.*

---

## 1. Résumé exécutif

Hermes v2 conserve le seul moteur de rendement défendable académiquement — momentum cross-sectionnel 12-1 + filtre TSMOM + vol-targeting conservateur — mais commence par **réparer trois garde-fous existants qui sont aujourd'hui du code mort** (le coupe-circuit de drawdown reçoit une courbe d'equity à un seul point dans `hermes/main.py:122` donc ne se déclenche jamais ; `trailing_stop_triggered` n'est appelé nulle part ; le « demi-Kelly » de `risk.py:61` est un no-op arithmétique `× 0,5 × 2`), et par **remplacer l'univers survivorship-biaisé** (20 méga-caps choisies en 2026) par les constituants point-in-time du S&P 500, seule façon de rendre le gate Deflated Sharpe/PBO non décoratif. L'IA (API Claude) n'a **aucun pouvoir d'achat et aucun chemin de code vers l'exécution** : elle occupe trois rôles bornés — sentinelle EDGAR en *second avis* derrière un filtre mécanique des items 8-K critiques (veto-only, exclusion vers le cash sans remplacement, plafonné, citation verbatim vérifiée par sous-chaîne, 6 mois de shadow mode évalué sur des critères de *qualité* et non de P&L), rapporteur hebdomadaire en français dont tous les chiffres sont calculés en Python, et analyste d'incidents — pour **moins de 1 €/mois, plafond dur à 5 €**. La couche production (supervisor idempotent par recalcul de delta vs positions broker, réconciliation pré/post consciente des corporate actions, IB Gateway dockerisé avec IBC, dead-man's switch externe healthchecks.io, alertes Telegram à trois niveaux) garantit que **toute panne fait retomber le système sur un état plus simple déjà validé** et que le silence de la machine est lui-même une alerte. La poche PEAD, le tilt de ton textuel et le RegimeFilter binaire sont **délibérément écartés** sur la base des critiques (espérance quasi nulle sur méga-caps, chantier XBRL point-in-time sous-budgété, puissance statistique nulle des protocoles d'évaluation proposés) ; l'attente de performance est calibrée sur la décroissance post-publication de −58 % (McLean & Pontiff), et 6 mois de paper trading IBKR minimum précèdent toute discussion — séparée et hors périmètre — d'argent réel.

---

## 2. Architecture retenue

### 2.1 Principe directeur

Trois plans étanches, chacun avec son sens de défaillance :

| Plan | Rôle | Sens de défaillance |
|---|---|---|
| **Quantitatif** (signal + risque + exécution) | Décide et trade | **fail-closed** sur données invalides : aucun ordre |
| **IA** (analyse) | Observe, réduit, explique | **fail-open** : panne IA → cycle quant pur identique |
| **Ops** (supervision) | Surveille tout, y compris lui-même | **dead-man's switch externe** : le silence alerte |

Aucun chemin de code ne va de l'API Claude vers `execution/`. L'IA produit des fichiers JSON versionnés, validés par schéma, consommés par la mécanique. Le mode dégradé de chaque couche EST le système plus simple déjà validé (principe cardinal salué par les 10 critiques).

### 2.2 Composants

**Existants conservés tels quels** : `hermes/strategy/momentum.py` (12-1, skip 1), `hermes/backtest/engine.py` + `validate.py` (walk-forward, DSR/PBO), `hermes/execution/ibkr_client.py` (triple verrou paper/réel, 45 msg/s), `hermes/reporting/tearsheet.py`, journal JSONL de `order_manager.py`.

**Existants corrigés** (Phase 0, détail §7) :
- `hermes/strategy/risk.py` — suppression du pseudo-Kelly (`scalar * kelly_fraction * 2` → `scalar` seul, documenté honnêtement : le sizing conservateur EST le vol-target 15 % + zéro levier + caps ; aucun Kelly n'est estimé, on cesse de le prétendre) ;
- `hermes/main.py` — la courbe d'equity vient d'un historique NAV persistant, plus jamais d'une série à un point ;
- `hermes/execution/order_manager.py` — quantités fractionnaires (IBKR fractional shares) pour rendre les poids cibles atteignables sur petit capital ;
- `hermes/config/settings.yaml` — `top_n: 10`, `max_position_weight: 0.15` (un top-5 à cap 30 % est un pari idiosyncratique, pas le momentum de la littérature — critique unanime), univers point-in-time (§4).

**Nouveaux** :

```
hermes/
├── data/
│   ├── sentinel.py          # DataSentinel fail-closed (validation avant tout calcul)
│   └── universe_pit.py      # constituants S&P 500 point-in-time (CSV versionné)
├── ops/
│   ├── supervisor.py        # machine à états du cycle mensuel, idempotente, TTL
│   ├── daily_check.py       # job quotidien LÉGER : NAV, stops (reduce-only), breaker, santé
│   ├── reconciler.py        # broker vs état local, pré+post, corporate actions
│   ├── alerting.py          # Telegram sortant 3 niveaux + poll /kill (timer 15 min)
│   └── state.py             # state/ : portfolio.json, nav_history.csv, cycle_state.json
├── intel/
│   ├── edgar_client.py      # SEC EDGAR : submissions + filings, cache disque, throttle
│   ├── mechanical_flags.py  # filtre DÉTERMINISTE items 8-K (4.02, 4.01, 3.01, 1.03)
│   └── sentinel_ai.py       # second avis Haiku (veto-only), citation vérifiée
├── ai/
│   ├── client.py            # client Claude, schémas Pydantic, retry, journalisation
│   ├── budget_guard.py      # compteur persistant, coupure dure à 5 €/mois
│   ├── digest.py            # rapport hebdo français (Sonnet), chiffres 100 % Python
│   └── golden_set.py        # non-régression sur 10 filings archivés à chaque
│                            #   changement de modèle/prompt
└── research/
    └── trials_registry.jsonl # registre append-only AUTOMATIQUE des essais (n_trials)
```

**État persistant** (`state/`, écriture atomique tmp+rename, sauvegarde quotidienne rclone **excluant `.env` et tokens**) : `portfolio.json` (positions attendues, plus-hauts par position pour les stops), `nav_history.csv` (NAV quotidienne — prérequis du coupe-circuit), `cycle_state.json` (étape courante du supervisor, horodatée, **périmée après 24 h** : reprise après crash = recalcul complet, jamais exécution de poids calculés sur des prix morts), `api_spend.json`.

### 2.3 Schéma des flux

```
             BOUCLE RECHERCHE (jamais connectée au broker)
  ┌────────────────────────────────────────────────────────────────┐
  │ univers PIT (CSV) → yfinance → backtest walk-forward           │
  │ (stops + breaker + ré-entrée SIMULÉS) → trials_registry.jsonl  │
  │ → gate DSR ≥ 0,90 / PBO ≤ 0,30 → tag git de la config          │
  └────────────────────────────────────────────────────────────────┘
                                │ config taguée
                                ▼
  QUOTIDIEN (systemd timer,     MENSUEL (supervisor.py, fenêtre de grâce 72 h,
  ~30 s, 18h30 ET,              retry J+1/J+2, calendrier NYSE)
  calendrier NYSE)              ┌──────────────────────────────────────────────┐
  ┌──────────────────────┐      │ FETCH ──► DataSentinel (fail-closed)         │
  │ NAV → nav_history    │      │   ──► momentum 12-1 ∩ TSMOM → candidats      │
  │ plus-hauts positions │      │   ──► [flags mécaniques 8-K ∪ veto IA]  ◄────┼── EDGAR
  │ stops 15 % (REDUCE-  │      │        (exclusion → CASH, jamais n+1)        │   (gratuit)
  │  ONLY, avec preflight)│     │   ──► inverse-vol + vol-target 15 % + caps   │
  │ breaker 15 % (bloque │      │   ──► PREFLIGHT (kill switch, breaker, NAV)  │
  │  les achats)         │      │   ──► RECONCILE_PRE ──► EXECUTE (delta vs    │
  │ healthcheck agrégé   │      │        positions broker = idempotence)       │
  │ ping healthchecks.io │      │   ──► RECONCILE_POST ──► REPORT              │
  └──────────┬───────────┘      └──────────────────┬───────────────────────────┘
             │                                     │
             ▼                                     ▼
     Telegram (INFO/WARN/          IB Gateway paper 4002 (Docker + IBC,
     CRITICAL) + hc-ping           restart quotidien géré) ──► IBKR paper
             ▲
             │  EN DÉRIVATION, JAMAIS EN SÉRIE :
     ┌───────┴────────────────────────────────────────────┐
     │ IA : digest hebdo (Sonnet) · sentinelle (Haiku)    │
     │ · incidents (Haiku) — JSON Pydantic, budget_guard, │
     │ panne = cycle identique sans IA (fail-open)        │
     └────────────────────────────────────────────────────┘
```

**Infra** : mini-PC domestique ou VPS ~5 €/mois, Docker Compose (`ib-gateway`+IBC ; `hermes` déclenché par systemd timers — pas de daemon 24/7). Coût total système annoncé honnêtement : **~5-7 €/mois** (infra ~5 € + API < 1 €), la contrainte « quelques €/mois d'API » étant respectée avec marge ×5.

---

## 3. L'étage IA en détail

**Doctrine** : l'IA n'est jamais un prédicteur de rendements (aucune claim NLP vérifiée au rapport, §2.5). Elle fait trois choses que les formules ne font pas : lire du texte réglementaire en second avis, expliquer le système en français, diagnostiquer des logs. Sa valeur principale est **opérationnelle** (rendre le système auditable et survivable par une personne seule), pas de l'alpha — positionnement du design « simplicité » validé par toutes les critiques.

### 3.1 Sentinelle EDGAR — veto en second avis (EXPÉRIMENTAL, shadow 6 mois)

La hiérarchie corrigée (critique majeure du design 1 : « mécanique d'abord, IA en second ») :

1. **Étage 0 — filtre mécanique, zéro IA, zéro coût** : `mechanical_flags.py` lit les **métadonnées structurées** de l'index EDGAR des 8-K des candidats (90 jours) : item 4.02 (non-reliance sur les états financiers), 4.01 (changement d'auditeur), 3.01 (risque de delisting), 1.03 (faillite). Ces items sont des champs de l'index — aucune hallucination possible. Item 4.02 ou 1.03 ⇒ **veto mécanique automatique** (actif dès le jour 1, ce n'est pas de l'IA).
2. **Étage 1 — Haiku en second avis** : uniquement pour (a) qualifier grave/anodin les 4.01 et 3.01, (b) chercher la mention *going concern* dans le dernier 10-K/10-Q. Appels **synchrones** (la Batch API est abandonnée : coordination J-1 fragile pour économiser des centimes — critique convergente), `max_retries=2`, timeout 60 s.

**Sortie structurée** (`client.messages.parse()` + Pydantic, `additionalProperties: false`) :

```json
{"ticker": "XYZ", "verdict": "RAS|GRAVE", 
 "categorie": "auditor_change|delisting|going_concern|RAS",
 "extrait_verbatim": "…", "form": "8-K", "accession": "0001234-26-000001"}
```

**Garde-fous (fusion des meilleurs patterns des 5 designs, corrigés)** :
- **Veto-only strict** : un veto retire le titre et son poids **va au cash** — jamais de remplacement par le rang n+1 (le remplacement ferait entrer un titre choisi de facto par l'IA — faille identifiée par la critique du design 5) ;
- **Citation verbatim vérifiée par sous-chaîne** (texte normalisé Unicode/espaces) contre le document source : pas de correspondance exacte ⇒ verdict ignoré + WARN (anti-hallucination mécanique, pas déclaratif) ;
- **Plafond 3 exclusions/cycle**, tri par **gravité factuelle de l'item** (1.03 > 4.02 > going_concern > 4.01 > 3.01), jamais par la « confidence » auto-déclarée du LLM (non calibrée — critique unanime, le champ confidence est supprimé du schéma) ;
- **Chaque exclusion notifiée Telegram** avec l'extrait pour revue humaine le jour même ;
- **Shadow mode 6 mois**, verdicts journalisés non appliqués, avec trois états distincts dans les logs : `analysé_OK` / `aucune_donnée` / `erreur` (un composant silencieusement mort ne doit pas ressembler à « rien à signaler ») ;
- **Critère d'activation = QUALITÉ, pas P&L** (l'A/B P&L sur ~6 cycles est statistiquement vide — consensus des critiques) : activation seulement si, sur 6 mois, 100 % des citations sont exactes, zéro classement « GRAVE » jugé infondé en revue humaine, zéro état `erreur` non expliqué. La double comptabilité quant-pur vs avec-veto est **conservée en journalisation permanente** mais étiquetée « indicative, sans valeur probante avant plusieurs années » ;
- L'IA ne voit **jamais** les tailles de positions ni le capital ; les filings EDGAR sont traités comme entrée non fiable (anti prompt-injection).

**Prompt système type (figé, versionné dans `hermes/intel/prompts/sentinel_v1.md`)** :
> « Tu es un analyste risque. À partir des extraits de dépôts SEC fournis UNIQUEMENT, détermine si l'événement est grave (menace la continuité ou la fiabilité des comptes) ou anodin (transition planifiée, formalité). Tu ne recommandes JAMAIS d'achat. En cas de doute, réponds RAS. Cite verbatim le passage exact qui justifie ton verdict. Si le passage n'existe pas, réponds RAS. »

### 3.2 Rapporteur hebdomadaire (Sonnet)

Chaque vendredi : collecte **mécanique** des métriques (NAV, drawdown, ES 97,5 % glissant, positions, écart paper-vs-backtest, incidents, dépense API, verdicts sentinelle) → JSON → un appel `claude-sonnet-4-6` → message Telegram. Règles dures :
- Le statut 🟢/🟠/🔴 en première ligne est décidé par **règle mécanique** (drawdown, réconciliation, erreurs, ES hors enveloppe) — le texte l'explique, ne le décide jamais ;
- **Tout chiffre du rapport vient d'un tableau calculé en Python et injecté tel quel** ; interdiction d'arithmétique nouvelle et de recommandations de changement de stratégie dans le prompt ;
- Phrase obligatoire du template tant que n < 12 mois : « aucune conclusion statistique n'est possible à cet horizon » ;
- `question_pour_humain: null` par défaut, remplie seulement sur anomalie mécaniquement détectée (anti-bruit rituel).

### 3.3 Analyste d'incident (Haiku, à la demande)

Sur alerte CRITICAL ou WARN répétée : les 200 dernières lignes de log pertinentes → `{diagnostic, gravite_estimee, action_suggeree}` joint au message Telegram. L'humain agit, jamais le bot.

### 3.4 Gouvernance des modèles et du budget

- **Modèles en config** (`ai.models.sentinel: claude-haiku-4-5`, `ai.models.digest: claude-sonnet-4-6`), jamais codés en dur ; modèle inconnu au démarrage ⇒ bascule quant pur + WARN ;
- **Golden set** : 10 filings archivés avec verdicts attendus, rejoués à chaque changement de modèle ou de prompt ; dérive ⇒ retour en shadow (répond à la faille « fenêtre de validité de l'instrument plus courte que la période de mesure ») ;
- **`budget_guard.py`** : compteur persistant alimenté par `response.usage`, coupure dure à **5 €/mois** ⇒ quant pur + WARN, règle « tout l'univers ou personne » par cycle (jamais de scoring partiel biaisant la coupe transversale) ; **doublé d'un spend limit configuré dans la console Anthropic** (le vrai garde-fou dur, le compteur local n'étant que la couche logicielle) ;
- Pas de prompt caching (sous le minimum cacheable de Haiku et inutile à cadence mensuelle), pas de Batch API.

### 3.5 Coût mensuel chiffré (tarifs vérifiés : Haiku 4.5 = 1 $/5 $ par MTok ; Sonnet 4.6 = 3 $/15 $)

| Usage | Volume/mois | Coût |
|---|---|---|
| Sentinelle Haiku (synchrone, post-filtre mécanique : ~3-8 filings signalés × ~6 k tokens) | ~50 k in / 3 k out | ~0,07 $ |
| Digest Sonnet (4 × ~7 k in / 1 k out) | ~28 k in / 4 k out | ~0,14 $ |
| Incidents Haiku | variable | ~0,03 $ |
| Golden set (amorti) | occasionnel | ~0,02 $ |
| **Total** | | **~0,25 $/mois ≈ 0,25 €** — plafond dur 5 € |

### 3.6 Mode dégradé

API Claude en panne, schéma invalide, citation non vérifiée, budget épuisé, modèle déprécié ⇒ **le cycle se déroule à l'identique en quant pur** (= Hermes v1 réparé), incident journalisé avec son état exact, WARN Telegram. L'IA ne peut ni bloquer un rebalancement, ni retarder un cycle, ni passer un ordre — elle est en dérivation, jamais en série.

---

## 4. Signaux retenus et justification académique

| Signal | Statut | Justification (renvois au rapport) |
|---|---|---|
| **Momentum cross-sectionnel 12-1, skip 1 mois, top 10, long-only** | Cœur, 100 % du capital | Seule anomalie ayant survécu hors-échantillon **après publication** (Jegadeesh & Titman 1993/2001 ; survey Wiest 2023 — §1.2), le critère qui la sépare des règles techniques réfutées (§1.1). Skip du dernier mois : short-term reversal documenté. **Correctif exigé par les critiques** : sur un univers **point-in-time** (constituants historiques S&P 500 reconstruits depuis les sources publiques, CSV `data/universe/sp500_constituents.csv` versionné) et non 20 gagnants de 2026 — DSR/PBO corrigent la sélection de stratégies, pas un univers contaminé ; top 10 avec cap 15 % pour se rapprocher de l'anomalie documentée (déciles diversifiés) au lieu d'un pari concentré à 5 lignes. |
| **Filtre TSMOM** (détenir seulement si rendement propre 12-1 > 0) | Cœur | Moskowitz-Ooi-Pedersen 2012, utilisé en **filtre de poche cash** uniquement — la version « signal par instrument » a été réfutée en vérification (§1.2) et est respectée comme telle. |
| **Vol-targeting conservateur continu** (inverse-vol + cible 15 %, plafonné à 1, zéro levier) | Cœur (sizing) | Barroso & Santa-Clara 2015 : le scaling **continu** par la vol réalisée de la stratégie quasi élimine les momentum crashes (§1.2). C'est précisément ce mécanisme — pas un RegimeFilter binaire à seuils (écarté, §8). Le vol-timing agressif est exclu (gains effondrés hors-échantillon, Cederburg 2020 — §7). |
| **Trailing stop 15 % + coupe-circuit drawdown 15 % + ré-entrée pré-enregistrée** | Contrôle de risque | Stops larges seulement (Lo & Remorov 2017 : les stops serrés détruisent de la valeur) ; les stops n'ajoutent de la valeur qu'en régime momentum (Kaminski & Lo 2014 — cohérent ici). **Rendus réels** : évalués quotidiennement par `daily_check.py` et **simulés dans le backtest** (le backtest doit tester la stratégie que la production exécute — faille corrigée). |
| **Flags mécaniques 8-K (4.02/1.03/4.01/3.01)** | Contrôle de risque, actif jour 1 | Pas un signal de rendement : réduction d'univers sur red flags comptables **objectifs et structurés** de l'index EDGAR (§4bis) — zéro IA, zéro hallucination possible. |
| **Sentinelle IA going-concern / qualification grave-anodin** | **EXPÉRIMENTAL**, shadow 6 mois, garde-fous renforcés (§3.1) | Aucune claim NLP vérifiée au rapport (§2.5) — assumé et étiqueté ; c'est une défense qualitative bornée, pas un alpha prétendu. |

**Attente calibrée** : une fraction des rendements académiques (décroissance post-publication −58 %, McLean & Pontiff — §2.1) ; Sharpe glissant 12 mois vs enveloppe du backtest revu chaque trimestre ; un ETF monde peut faire mieux — le projet est autant un apprentissage instrumenté qu'une machine à alpha (honnêteté reprise du design 4).

---

## 5. Gestion du risque et garde-fous (défense en profondeur)

**Couche 1 — Données (fail-closed)** : `DataSentinel` valide avant tout calcul — prix > 0, NaN < 5 %/titre, fraîcheur selon **calendrier NYSE** (`exchange_calendars`, plus de faux WARN les week-ends de 3 jours), |variation jour| < 40 % croisée avec les corporate actions yfinance ; échec ⇒ HALT, aucun ordre, alerte. **Abandonné** : le cross-check bloquant yfinance-vs-IBKR à 2 % (faux HALT récurrents aux dates ex-dividende — critique convergente) ; remplacé par un log mensuel non bloquant de l'écart de signal entre les deux sources.

**Couche 2 — Sizing** : inverse-vol 60 j, cible de vol 15 % (continu), cap 15 %/position, top 10, zéro levier, fractional shares (poids cibles atteignables sur petit capital — corrige l'artefact d'arrondi `int()` qui polluait la réconciliation).

**Couche 3 — Stops et coupe-circuits, désormais réels** :
- `daily_check.py` (quotidien, ~30 s) maintient `nav_history.csv` et les plus-hauts par position ; stop 15 % franchi ⇒ ordre de **vente uniquement** (le job quotidien est *reduce-only par construction* — même asymétrie que l'IA), avec preflight complet ;
- coupe-circuit : drawdown NAV ≥ 15 % ⇒ blocage de tout achat + alerte CRITICAL ; les stops restent actifs ;
- **ré-entrée pré-enregistrée** (comble le trou majeur identifié par 4 critiques : la décision la plus dangereuse ne doit pas être émotionnelle) : reprise au premier rebalancement mensuel où le drawdown est repassé < 10 % (hystérésis), à 50 % de l'exposition cible le premier mois puis 100 % — règle simple, écrite à l'avance, **simulée dans le backtest**.

**Couche 4 — Exécution** : preflight (kill switch fichier, coupe-circuit, NAV cohérente) avant tout ordre ; idempotence par **recalcul du delta vs positions broker réelles** (la primitive déjà présente dans `compute_orders` — pas d'exclusion fragile des `order_sent` loggés) ; `cycle_state.json` périmé après 24 h ⇒ recalcul complet ; fenêtre de grâce 72 h avec retry J+1/J+2 (jamais J+30) ; réconciliation pré ET post, seuils DRIFT (WARN) / CRITICAL (auto-création du KILL_SWITCH), **consciente des corporate actions** (un split 10:1 détecté par cohérence quantité×prix ⇒ mise à jour d'état, pas un faux CRITICAL) ; seuils calibrés sur 2 cycles de dry-run avant d'armer l'auto-kill (anti fatigue d'alerte).

**Couche 5 — IA bornée** : asymétrie structurelle (réduire/exclure vers le cash uniquement), plafond 3 vetos, citation vérifiée mécaniquement, shadow d'abord, fail-open, budget coupé à 5 €, aucun accès au client IBKR ni aux tailles de positions.

**Couche 6 — Humain** : KILL_SWITCH fichier (création à distance via `/kill` Telegram **pollé toutes les 15 min par timer** — latence assumée et documentée, allowlist de `chat_id`, l'arrêt d'urgence immédiat reste SSH ; réarmement uniquement par accès shell délibéré) ; double verrou paper/réel existant (`account_type` + `HERMES_LIVE_ACKNOWLEDGED`) intact ; runbook d'une page par type d'alerte, **incluant la procédure de sortie de HALT**.

**Couche 7 — Anti-illusion statistique** : registre `trials_registry.jsonl` **écrit automatiquement par le harnais de backtest** (hash de config à chaque run — l'honnêteté du n_trials devient mécanique, plus déclarative), initialisé à `n_trials: 10` pour les degrés de liberté historiques déjà consommés ; DSR ≥ 0,90 et PBO ≤ 0,30 requis avant toute connexion broker ; ES 97,5 % historique glissant au tearsheet (Artzner 1999 — §8bis), ES hors enveloppe du backtest ⇒ statut 🟠 forcé + item obligatoire du digest + revue humaine (pas de nouvelle règle automatique paramétrée : l'action dure reste le coupe-circuit, on n'ajoute pas de paramètres overfittables).

---

## 6. Monitoring & exploitation (5 min/semaine)

**Quotidien (0 min humaine)** : `daily_check.py` → une ligne de heartbeat + ping `hc-ping.com`. Machine morte, cron cassé, réseau coupé ⇒ **healthchecks.io alerte par email** (le silence n'est jamais « tout va bien »). IB Gateway : Docker + IBC gère login auto et restart quotidien imposé par IBKR ; watchdog de connexion avec backoff. Une session TWS manuelle concurrente qui déconnecte le Gateway est documentée au runbook comme cause de WARN bénin.

**Hebdomadaire (5 min)** : lire le digest Telegram du vendredi. Première ligne 🟢/🟠/🔴 mécanique. 🟢 = rien d'autre à faire. 🟠 = lire les anomalies listées (chiffres Python, prose Claude). 🔴 = suivre le runbook, l'analyste d'incident a déjà joint son diagnostic.

**Mensuel (15 min)** : vérifier dans le digest post-rebalancement : ordres vs dry-run diffé, réconciliation MATCHED, dépense API, verdicts sentinelle (+ extraits), taux d'états `erreur`/`aucune_donnée` de la couche IA.

**Trimestriel (1 h)** : revue de décroissance — Sharpe glissant 12 mois vs enveloppe walk-forward, ES vs enveloppe, écart paper-vs-backtest (en gardant en tête l'artefact de sources yfinance/IBKR, loggé séparément), bilan qualité de la sentinelle. Opérationnalise McLean-Pontiff.

**Déploiement/rollback** : code taggé git ; `deploy.sh` = checkout tag → `pytest` (30 tests existants + nouveaux, jamais cassés) → `paper --dry-run` diffé contre le dernier cycle → activation. Rollback = même script, tag précédent. Sauvegarde quotidienne `state/` + `logs/` par rclone (secrets exclus).

---

## 7. Plan d'implémentation

Ordre corrigé selon la critique la plus structurante : **réparer le socle d'abord, déployer tôt en paper (seul générateur d'apprentissage réel), l'IA en dernier**. Calendrier honnête pour un non-expert seul : **~3-4 mois**, pas 7 semaines. Chaque étape se termine par `pytest` vert et un tag git.

**Étape 0 — Audit correctif du socle (2 semaines)** — ON MODIFIE :
1. `risk.py` : suppression du no-op `× kelly_fraction × 2` ; docstring honnête (« sizing = vol-target + caps + zéro levier ; aucun Kelly estimé »).
2. `hermes/ops/state.py` + `daily_check.py` : NAV quotidienne persistée, plus-hauts par position, évaluation quotidienne stops (reduce-only) et coupe-circuit ; `main.py:122` branché sur `nav_history.csv`.
3. `backtest/engine.py` : simulation des trailing stops, du coupe-circuit et de la règle de ré-entrée (le backtest teste la stratégie réellement exécutée).
4. `order_manager.py` : fractional shares ; test d'intégration `cmd_paper` complet avec client IBKR mocké (fills partiels, rejets, crash mi-cycle) — la zone où vivaient les bugs de code mort.
   *Test de sortie : un backtest où le breaker se déclenche puis ré-entre ; un cycle paper simulé où un stop vend.*

**Étape 1 — Premier déploiement paper minimal (1 semaine, en parallèle)** — ON GARDE le pipeline existant réparé :
5. Mini-PC/VPS, Docker Compose ib-gateway+IBC (port 4002), timers systemd, healthchecks.io, Telegram sortant minimal. Dry-runs 2 semaines, test du KILL_SWITCH, calibration des seuils de réconciliation sur le drift observé. Cycles paper réels ensuite — **statut : test de plomberie**, pas de validation de signal (l'univers est encore biaisé).

**Étape 2 — Univers point-in-time + re-validation (3 semaines)** — ON AJOUTE :
6. `data/universe_pit.py` + CSV des constituants S&P 500 historiques ; filtre liquidité ; documentation du biais résiduel (titres radiés sans prix yfinance).
7. `trials_registry.jsonl` automatique dans le harnais ; backtest 2010-2026 à coûts réalistes (bps + **commissions minimales fixes IBKR** modélisées) ; gate DSR/PBO ; bascule de la config de production sur l'univers PIT, top 10, cap 15 %.
   *Critère d'arrêt hérité du design 1 : si la config élargie ne passe pas le gate, on reste sur la config courante en la déclarant explicitement « non validée académiquement, plomberie seulement » — le design survit à l'échec de sa propre extension.*

**Étape 3 — Couche ops complète (2-3 semaines)** — ON AJOUTE :
8. `supervisor.py` (machine à états, écriture atomique, TTL 24 h, test « crash à chaque étape puis reprise, zéro double ordre par recalcul de delta »), `reconciler.py` (corporate actions), `alerting.py` (3 niveaux, poll `/kill` 15 min, allowlist), fenêtre de grâce 72 h avec calendrier NYSE, runbook.

**Étape 4 — IA v1 : rapporteur + incidents (1-2 semaines)** — ON AJOUTE :
9. `hermes/ai/` : client + Pydantic + `budget_guard` + `digest.py` + incident. Tests avec réponses mockées (valide, invalide, timeout, refus, budget dépassé ⇒ toujours quant pur). Spend limit console Anthropic configuré.

**Étape 5 — IA v2 : sentinelle EDGAR (2 semaines)** — ON AJOUTE :
10. `edgar_client.py` (User-Agent « HermesBot dylan.cardoso.pires@gmail.com », throttle 8 req/s, cache disque avec `acceptance_datetime`), `mechanical_flags.py` (actif immédiatement), `sentinel_ai.py` en **shadow**, golden set archivé.

**Étape 6 — Régime de croisière (mois 3 → 9)** :
11. 6 mois de paper minimum sur la config validée. Bilan à 6 mois : performance vs enveloppe, incidents, qualité sentinelle ⇒ décisions humaines explicites : (a) activer le veto IA (critères qualité §3.1), (b) élargir/ajuster, (c) toute considération d'argent réel = décision séparée, explicite, hors périmètre de ce design.

---

## 8. Ce qui a été délibérément écarté et pourquoi

| Écarté | Origine | Arguments des critiques retenus |
|---|---|---|
| **Poche PEAD avec capital** (design 1) | quant-rigoureux | Triple défaut cumulatif : edge quasi nul sur méga-caps (l'anomalie vit dans les small caps illiquides), chaîne temporelle incohérente (le XBRL arrive 2-4 semaines après le 8-K ⇒ le fail-safe de cross-check est inopérant au moment de la décision, et le drift est consommé avant l'entrée), chantier XBRL point-in-time (EPS Q4 dérivé, restatements, splits) sous-budgété d'un facteur 3-5, quintiles de ~10 titres sans puissance pour DSR/PBO, commissions fixes IBKR sur petits tickets. ~80 % de la complexité nouvelle pour une espérance quasi nulle. **Ré-ouvrable seulement** après élargissement de l'univers + résolution du XBRL PIT, comme projet de recherche séparé. |
| **Tilt de ton / Lazy Prices en shadow** (designs 1-2) | quant + ia-max | ~80 observations en 24 mois = aucune puissance statistique, promotion promise inatteignable, code mort à maintenir. On ne construit pas ce qu'on ne pourra jamais valider. |
| **Veto Opus mensuel** (design 1) | quant | Les items 8-K critiques sont des **métadonnées structurées** gratuites — payer Opus pour les lire inverse la hiérarchie ; cadence mensuelle vidant la fonction de son sens ; le rejeu historique « qualitatif » est du biais rétrospectif. Remplacé par le filtre mécanique + Haiku en second avis. |
| **RegimeFilter binaire bear+vol** (design 3) | risque-sécurité | Défend le mauvais risque (les crashes de Daniel & Moskowitz frappent la jambe short, inexistante en long-only), réduit précisément au rebond, 2 paramètres overfittables non validables (3-4 déclenchements en 20 ans), interaction non analysée avec les 3 couches de dé-levier existantes. Le vol-targeting **continu** existant est le mécanisme réellement documenté par Barroso & Santa-Clara. |
| **Batch API + prompt caching** | tous | Économise des centimes, ajoute deux crons couplés, du polling, des résultats en retard précisément en saison de résultats ; instructions sous le minimum cacheable de Haiku (4096 tokens). Synchrone + retry SDK. |
| **Remplacement n+1 après veto** (designs 2-5) | ia-max, prod-ops | Un faux positif ferait *entrer* un titre choisi de facto par l'IA — brise l'asymétrie. Exclusion vers le cash uniquement. |
| **Activation du veto sur contrefactuel P&L** (designs 2-4) | tous | ~10-18 événements en 6 mois = pile ou face ; c'est le data-snooping par la porte de derrière (Rink 2023). Critères de qualité vérifiables à la main. |
| **Cross-check bloquant yfinance/IBKR à 2 %** (design 3) | risque-sécurité | Faux HALT récurrents aux ex-dividendes ; réintroduit yfinance en dépendance de production. Dégradé en log informatif mensuel. |
| **Idempotence par exclusion des `order_sent`** (design 5) | prod-ops | `order_sent` ≠ fill ; fragile aux rejets/fills partiels/crashs. Recalcul du delta vs positions broker (déjà la primitive du code). |
| **Commandes Telegram via daemon 24/7** (design 5) | prod-ops | Contradiction avec « pas de daemon » ; troisième service à sécuriser. Poll 15 min + allowlist, latence documentée, urgence = SSH. |
| **ML prédictif (Gu-Kelly-Xiu), indicateurs techniques seuls, sentiment réseaux sociaux, vol-timing agressif, multi-marchés, extraction de guidance** | tous | Respectivement : overfitting démultiplié et inmaintenable en solo ; réfutés (§1.1, data-snooping + coûts) ; zéro claim vérifiée ; gains effondrés hors-échantillon (§7) ; 83 % des anomalies US échouent ailleurs (§8) ; champ invérifiable n'alimentant aucun signal validé. |

---

## 9. Risques résiduels assumés

1. **Survivorship résiduel dans les prix** : l'univers point-in-time corrige l'appartenance, mais yfinance n'a pas l'historique des titres radiés — le backtest reste optimiste dans une mesure documentée. Mitigation partielle (haircut d'attentes −58 % et plus), pas élimination ; des données payantes point-in-time restent la seule solution complète, hors budget actuel.
2. **Un top 10 long-only sur le S&P 500 n'est toujours pas les déciles de milliers de titres de la littérature** : l'espérance d'alpha du cœur est modeste et peut être nulle ; l'ETF monde comme référence honnête figure au digest.
3. **Momentum crashes résiduels** : le vol-targeting atténue, n'élimine pas ; le coupe-circuit peut cristalliser une perte avant un rebond — la règle de ré-entrée pré-enregistrée borne le dégât comportemental, pas le dégât de marché.
4. **La valeur de la sentinelle IA est possiblement nulle et restera longtemps inmesurable** en P&L (taux de base des red flags quasi nul sur cet univers) : assumé — elle est bornée, quasi gratuite, coupée sans état d'âme si la revue qualité déçoit ; sa vraie valeur est le rapporteur.
5. **Paper ≠ réel** : fills paper IBKR optimistes, données éventuellement différées sans souscription — l'écart paper-vs-live est un gap documenté du rapport (§6) ; toute décision d'argent réel devra le réévaluer.
6. **Mono-machine, opérateur unique non expert** : au pire un rebalancement manqué (fenêtre 72 h + dead-man's switch), jamais une perte de contrôle ; mais IBC/Gateway casseront un jour, et la discipline (ne pas activer les flags avant l'heure, ne pas bricoler les prompts sans golden set, incrémenter le registre) repose in fine sur l'humain — le registre automatique et le runbook réduisent, ne suppriment pas.
7. **Dépendances non contractuelles** : yfinance (recherche), formats EDGAR, dépréciations de modèles Claude — couverts par fail-open, golden set et config, mais chaque cassure coûtera des heures de maintenance imprévues.
8. **Concentration factorielle** : un seul moteur de rendement ; la diversification value/quality est un renoncement de simplicité assumé, pas une limite d'ambition.