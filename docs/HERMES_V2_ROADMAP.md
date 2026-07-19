# Hermes v2 Sentinelle — Roadmap finale des améliorations

*Synthèse de l'architecte en chef, après passage de 39 idées (6 axes) au crible d'un critique adversarial. 24 retenues (dont 19 modifiées), 15 rejetées. Contraintes invariantes : budget quelques €/mois, paper trading IBKR, IA analyste sans aucun pouvoir d'ordre, maintenable par une personne seule.*

---

## 1. Résumé exécutif

**Un.** Le gate statistique sur lequel repose tout le design v2 (DSR ≥ 0,90 / PBO ≤ 0,30) est aujourd'hui structurellement complaisant — Sharpe calculé sans taux sans risque (`hermes/backtest/validate.py`), PBO jamais alimenté en multi-configs, n_trials déclaratif — et le rendre honnête coûte quelques jours, pas des semaines. **Deux.** L'univers S&P 500 point-in-time, prérequis bloquant de toute validation, est exigé par le design mais jamais construit : une source unique auditée + 15-20 dates charnières figées en tests unitaires le débloquent en moins d'une semaine. **Trois.** L'extraction d'un cœur de décision pur unique `decide()` appelé à l'identique par le backtest et la production (emprunt conceptuel à NautilusTrader), protégé par un backtest de non-régression sur dataset gelé, supprime structurellement la classe de bugs la plus dangereuse pour un opérateur seul — la divergence silencieuse recherche/prod. **Quatre.** La sentinelle EDGAR se renforce à coût quasi nul par trois extensions qui réutilisent la machinerie existante : pré-filtre full-text déterministe + golden set historique étiqueté, surveillance intra-mois des positions détenues (alerte mécanique par type d'item 8-K), et red team anti-injection du golden set. **Cinq.** Le maillon faible assumé du design étant la discipline humaine (§9.6), les trois outils qui la soutiennent — journal de décision explicable, assistant de revue trimestrielle pré-rempli, enveloppe bootstrap rendant mécaniques les seuils 🟢/🟠/🔴 — valent plus que tout nouveau signal.

---

## 2. QUICK WINS (haute valeur, effort en jours, risque faible)

### QW-1 — Taux sans risque réel dans Sharpe/DSR/tearsheet
- **Quoi** : brancher un taux sans risque (T-Bill 3 mois via `^IRX` sur yfinance — déjà dans la stack, zéro clé API ; FRED seulement si `^IRX` déçoit à l'audit) dans le calcul d'excès de rendement de `sharpe_ratio()` (`hermes/backtest/validate.py`), du DSR et du tearsheet. Re-passer le gate après correction et journaliser le run dans `trials_registry.jsonl`.
- **Pourquoi** : sur 2010-2026, ignorer l'écart entre l'ère à 0 % et l'ère à 5 % gonfle mécaniquement le Sharpe de fin de période, donc le DSR — le gate central du design est complaisant.
- **Corpus** : design v2 §5 couche 7 (le gate) ; défaut vérifié dans le code par le critique.
- **Effort** : 1-2 jours. **Garde-fous** : aucun paramètre nouveau ; run de re-validation compté au registre.

### QW-2 — Univers S&P 500 point-in-time : construction concrète
- **Quoi** : construire le CSV versionné exigé par `data/universe_pit.py` depuis **une** source primaire (dataset `fja05680/sp500` — à auditer : licence, méthodologie, couverture 2010-2026), validée par **échantillonnage manuel** de 15-20 dates charnières (Tesla déc. 2020, GM 2009, faillites) contre les communiqués S&P, figées en tests unitaires. Documenter le biais résiduel par ticker radié sans prix.
- **Pourquoi** : prérequis bloquant de toute la validation DSR/PBO ; le design l'exige (§4) sans dire comment.
- **Corpus** : design v2 §4 et §9.1. Source fja05680 : hors corpus, à auditer.
- **Effort** : 3-5 jours. **Garde-fous** : pas de « double source » illusoire (le diff Wikipedia-revisions a été rejeté : dérivés de la même source, parsing fragile).

### QW-3 — EDGAR Full-Text Search : pré-filtre going-concern + golden set historique
- **Quoi** : (a) avant tout appel Haiku, requête FTS exacte (`"substantial doubt" "going concern"`, formule standardisée ASC 205-40) restreinte au CIK et au dernier 10-K/10-Q — zéro hit = pas d'appel IA ; un hit = extrait exact fourni à Haiku, ce qui simplifie la vérification par sous-chaîne. (b) Constituer le golden set avec des positifs réels (10-K/10-Q pré-faillite : Lehman, Hertz, Bed Bath & Beyond) et des négatifs (boilerplate), **plus un cas type SVB** — instructif parce qu'il n'y avait *pas* de going-concern pré-effondrement : il calibre ce que la sentinelle ne peut pas voir.
- **Corpus** : cycle 4bis (FTS vérifié 3-0 : couverture 2001+, exhibits, 10 req/s + User-Agent) ; design v2 §3.1 (mécanique d'abord) et §3.4 (golden set sans méthode de constitution).
- **Effort** : jours. **Garde-fous** : vérifier le délai d'indexation FTS d'un dépôt frais ; si non indexé, fallback vers le chemin actuel (fail-open).

### QW-4 — Sentinelle intra-mois sur les positions détenues
- **Quoi** : `daily_check.py` interroge l'index EDGAR des 8-K des ~10 positions détenues (métadonnées structurées, zéro IA sur le chemin critique). Niveau d'alerte fixé **mécaniquement par le type d'item** (1.03/4.02 ⇒ CRITICAL ; 4.01/3.01 ⇒ WARN). Le verdict Haiku grave/anodin est joint en annotation étiquetée « shadow — indicatif » tant que la sentinelle n'est pas promue, et ne peut jamais rétrograder ni supprimer une alerte. Aucune vente automatique — décision humaine ou cycle mensuel.
- **Pourquoi** : angle mort temporel réel — un 8-K critique déposé à J+1 du rebalancement reste invisible ~30 jours hors mouvement de prix. Complément du trailing stop (qui capte le prix, pas le *pourquoi*), pas remplacement.
- **Corpus** : design v2 §3.1 et §5 couche 3 ; cycle 4bis (API submissions <1 s, gratuite).
- **Effort** : jours. **Coût** : ~0,02 $/mois. **Garde-fous** : mêmes trois états analysé_OK/aucune_donnée/erreur ; protocole shadow respecté.

### QW-5 — Journal de décision explicable + narration mensuelle
- **Quoi** : à chaque rebalancement, le supervisor persiste `state/decisions/YYYY-MM.json` **100 % mécanique** : pour chaque titre de l'univers — score momentum 12-1, rang, filtre TSMOM, flags 8-K, veto sentinelle (avec extrait), poids brut inverse-vol, poids final après vol-target/caps ; pour les sortants, la cause exacte. Une narration Haiku est générée **une fois par rebalancement** et jointe au digest existant (« NVDA entre : rang 3/500, 12-1 de +42 %, poids plafonné à 15 % »), avec vérification sous-chaîne de tous les chiffres et regex de vocabulaire interdit (aucune recommandation). Pas de commande interactive `/explain` au départ.
- **Pourquoi** : les valeurs intermédiaires sont aujourd'hui calculées puis jetées ; les persister sert la confiance de l'opérateur (§9.6), l'audit des vetos IA (§3.1) et le debugging de la réconciliation. Ne pas injecter les 500 lignes dans le prompt : top ~20 + mouvements seulement.
- **Corpus** : design v2 §3.1, §3.2 (« tout chiffre vient d'un tableau Python »), §2.1 ; cycle 8bis.
- **Effort** : jours (persistance de données existantes). **Coût IA** : ~0,05 $/mois.

### QW-6 — Enveloppe statistique par block bootstrap, centrée sur l'attente calibrée
- **Quoi** : block bootstrap (blocs ~3 mois, numpy pur — pas de vectorbt) des rendements du backtest validé, **après application du haircut McLean-Pontiff −58 % pré-enregistré**, 1 000-10 000 rééchantillonnages → percentiles pré-enregistrés de Sharpe glissant 12 mois, max drawdown, ES 97,5 %, écrits dans `state/backtest_envelope.json` versionné au tag git de la config. Paper sous percentile 20 = 🟠 forcé ; sous percentile 5 = 🔴 + revue. Pré-enregistrer aussi le taux de fausses alertes accepté (« percentile 20 = un trimestre 🟠 sur cinq même si tout va bien » — écrit dans settings.yaml pour que le futur soi ne panique pas).
- **Pourquoi** : trois mécanismes de gouvernance du design (§4, §5 couche 7, §6) invoquent une « enveloppe » jamais définie ; bootstrapper le backtest *brut* placerait la barre là où le paper est prévu de la rater (haircut) et produirait des 🔴 chroniques.
- **Corpus** : rapport §1.1 (Brock, Lakonishok & LeBaron) ; design v2 §4/§5/§6 ; méthode block bootstrap : hors corpus (standard), à vérifier.
- **Effort** : jours. **Garde-fous** : c'est de la mesure, pas du signal — zéro paramètre côté stratégie.

### QW-7 — Backtest de non-régression figé
- **Quoi** : parquet de prix committé (~15 tickers × 5 ans), `run_backtest` en pytest, courbe d'equity comparée à une référence. **Deux niveaux de tolérance** : stricte (atol=0) quand le lockfile de dépendances n'a pas bougé ; relative documentée (~1e-6) après montée de version, avec procédure au runbook (écart > 1e-6 = changement de comportement à investiguer ; sinon régénérer la référence dans un commit dédié ne contenant *que* ce changement). Versions épinglées dans requirements.
- **Pourquoi** : le bug « chiffres différents mais plausibles, aucun crash » est le plus sournois pour une personne seule ; filet indispensable du chantier de parité (CM-1). La tolérance 1e-9 initialement proposée aurait crié faux à chaque `pip install -U` (pandas 3 arrive, cycle 5) — un test qu'on apprend à ignorer.
- **Corpus** : cycle 5 §2.1-2.2 (déterminisme LEAN/Nautilus, inspiration) ; design v2 §6 (pytest avant activation), §3.4 (pattern golden set transposé).
- **Effort** : jours.

### QW-8 — Registre d'essais v2 branché sur le DSR
- **Quoi** : (1) `validate_strategy()` lit `trials_registry.jsonl` au lieu de recevoir n_trials en argument manuel — **n_trials = total des essais du registre, jamais un sous-ensemble par « famille »** (le clustering par famille sous-estimerait la déflation : porte dérobée supprimée) ; (2) variance **empirique** des Sharpes enregistrés injectée dans le DSR (conforme Bailey & López de Prado, au lieu de l'approximation sous H0) ; (3) champs enrichis par ligne : commit git, hash SHA-256 des données d'entrée, seed, métriques, chemin d'artefacts ; (4) champ `hypothese` obligatoire pré-run — sans lui, run marqué `exploratoire`, compté mais jamais promouvable. Règle de comptage **pré-enregistrée** : même config + mêmes données = non compté ; même config + données rafraîchies = compté une fois par millésime (yfinance réécrit silencieusement l'historique) ; config nouvelle = essai plein.
- **Corpus** : cycle 8bis §A (le DSR corrige « étant donné le nombre d'essais » — mesuré, pas déclaré) ; design v2 §5 couche 7 (promesse existante, non câblée — vérifié dans le code) ; cycle 5 §3.1 (concept workflow-recorder Qlib, sans adopter Qlib).
- **Effort** : 2-3 jours (~100 lignes, zéro dépendance).

### QW-9 — Red team anti-injection du golden set
- **Quoi** : génération one-shot par Sonnet de ~20 variantes synthétiques de 8-K piégés (instructions injectées, going-concern ambigus, faux passages à citer, homoglyphes unicode), verdict attendu RAS pour toutes les injections, ajoutées au golden set et rejouées à chaque changement de modèle/prompt. Étiquetées SYNTHÉTIQUES, jamais mélangées aux vrais filings dans les stats. **Set figé après génération** — pas de course aux armements que personne ne maintiendra seul.
- **Pourquoi** : la vérification par sous-chaîne est contournable par un document qui contient lui-même le passage qu'il veut faire citer ; ce harnais mesure le risque au lieu de le déclarer maîtrisé. Ne pas en tirer un faux confort : des attaques générées par Sonnet sont plus faibles que des attaques réelles.
- **Corpus** : design v2 §3.1 (entrée non fiable), §3.4 (échec golden set ⇒ retour en shadow — règle existante réutilisée).
- **Effort** : jours. **Coût** : ~0,50 $ one-shot, récurrent ~0.

### QW-10 — Banc de validation statistique complémentaire (4 tests, moteur existant)
Quatre tests indépendants, tous en jours, tous réutilisant le moteur pandas tel quel :
- **(a) Stress tests historiques nommés** : COVID févr-avr 2020 et bear market 2022 rejoués avec la stack de production complète (stops, breaker, ré-entrée, vol-target) ; rapport automatique (date de déclenchement du breaker, coût de la ré-entrée vs rester investi, whipsaws) ; diff archivé au registre à chaque changement de paramètre de risque. **Pas de rejeu 2008-2009** : yfinance n'a pas les radiés massifs de cette période — un chiffre faux serait pire que pas de chiffre ; le momentum crash type 2009 est remplacé par un scénario **synthétique explicitement étiqueté** (+30 % en 3 mois sur les perdants). *(Corpus : Daniel & Moskowitz 2016, Barroso & Santa-Clara 2015 §1.2 ; Kaminski & Lo cycle 7 ; §9.3 du design jamais chiffré.)*
- **(b) Test de permutation apparié en turnover** : 1 000+ portefeuilles aléatoires, même univers PIT, mêmes contraintes (top 10, cap 15 %, overlay, coûts) et **turnover contraint** à celui de la stratégie (schéma de rotation partielle : garder k titres, retirer 10-k) ; p-value empirique, gate p < 0,10. Complémentaire au DSR : la permutation teste si la config bat le hasard structuré, le DSR corrige la sélection parmi les essais. Effort réaliste : 3-5 jours. *(Corpus : §1.4 White/Hansen, §3.5 Hsu & Kuan, §1.1 Brock et al.)*
- **(c) Sensibilité au jour de rebalancement + micro-bruit** : 21 décalages J+0…J+20 et bruit ±5-10 bps ; la config passe si le Sharpe **médian** des 21 variantes reste au-dessus du seuil (on valide la stratégie, pas un calendrier chanceux) ; pas de gonflement de n_trials (diagnostic, pas sélection). *(Corpus : §1.2 Gong, Liu & Liu sur l'écho de Novy-Marx ; §1.4 Rink 2023.)*
- **(d) Chemins OOS combinatoires avec embargo court** : version corrigée du CPCV — N chemins OOS (distribution de Sharpe au lieu d'un point) avec **embargo 1-2 mois, sans purge de 12 mois** (les rendements de stratégie réalisés ne fuient pas comme des labels ML ; purger 12 mois sur ~180 observations viderait le test). *(Corpus : gap explicite cycle 3 §3.5/3.6 ; calibration : hors corpus, documentée.)*

### QW-11 — Ops & pilotage légers
- **(a) Calendrier d'earnings dérivé d'EDGAR** : rétrospectif exact via 8-K item 2.02 → `daily_check` annote toute alerte stop/NAV/réconciliation (« publication de résultats à J-1/J0 ») ; fenêtre prévisionnelle par périodicité des 10-Q → ligne du digest « positions publiant sous ~7 jours ». Pas de volet sentinelle (redondant : l'API submissions donne déjà la fraîcheur des dépôts), pas de calendrier externe. 2-3 jours. *(Cycle 4bis ; design §5 couche 3.)*
- **(b) Préavis J-1 mécanique** : dry-run diffusé la veille de la **première** tentative du calendrier (momentum, TSMOM, flags 8-K, poids cibles — **aucun appel IA en J-1**, les vetos sentinelle restent du jour J pour éviter les incohérences J-1/J), strictement fail-open (échec = WARN, le cycle s'exécute quoi qu'il arrive), mention que retry J+1/J+2 peut décaler l'exécution. Le diff prévisionnel-vs-réel est journalisé (métrique gratuite de stabilité). *(Design §6, §5 couche 6 ; cycle 8bis.)*
- **(c) Commandes Telegram lecture seule** : `/statut`, `/positions`, `/decisions`, `/budget_api` sur le poll 15 min existant, allowlist chat_id, fichiers sentinelles, zéro chemin nouveau vers `execution/`, toutes journalisées. **Pas de `/pause_achats`** (rejeté — cf. §5). L'échelle d'intervention reste binaire : rien, ou `/kill`. *(Design §5 couche 6, §8, §2.1.)*
- **(d) Registre des interventions humaines** : `state/interventions.jsonl` (horodatage + motif obligatoire demandé par Telegram) pour KILL_SWITCH, pauses, cycles sautés. Le contrefactuel chiffré est calculé **à la demande** lors de la revue trimestrielle (rejeu batch avec le moteur existant sur les poids cibles archivés du journal de décision) — pas de NAV fantôme permanente. *(Cycle 8bis Barber & Odean ; design §3.1.)*
- **(e) Âge des données partout** : chaque information de `/statut` et du dashboard affiche son âge (« NAV : il y a 4 h », « dernier contact EDGAR : 3 j ») avec seuil de péremption visuel. Fire-drill du chemin entrant (`/ping` validant poll + allowlist — le chemin de `/kill`, jamais re-testé après l'étape 1) : cadence **trimestrielle**, premier item de la checklist de revue existante ; absence de test = WARN au digest, jamais d'escalade email. *(Design §6, §7 étape 1, §3.1.)*

### QW-12 — Mesures de risque en numpy, Riskfolio comme oracle de test
- **Quoi** : ES 97,5 % historique, CDaR et Ulcer Index en ~30 lignes numpy dans `tearsheet.py`, avec tests unitaires dont les valeurs attendues sont générées **une fois** par Riskfolio-Lib dans l'environnement de recherche (la bibliothèque sert d'oracle, jamais de dépendance de prod — pas de CVXPY dans le chemin de production). Ajouter au registre §8 des écartés : une ligne HRP (« ré-ouvrable si l'univers de détention dépasse ~20 positions », zéro code) et l'entrée Black-Litterman (rejet doctrinal : les seules « views » possibles seraient IA → violation frontale du §3).
- **Corpus** : cycle 5 §3.2 ; design v2 §5 couche 7, §3, §8.
- **Effort** : 1-2 jours.

---

## 3. CHANTIERS MOYENS (effort en semaines)

### CM-1 — Parité recherche/production : cœur de décision unique + rejeu déterministe ⭐ prioritaire
- **Quoi** : extraire une fonction pure `decide(market_window, portfolio_state, flags) -> target_weights` encapsulant tout le chemin (momentum ∩ TSMOM → vetos → inverse-vol + vol-target + caps → stops/breaker/ré-entrée), appelée à l'identique par `engine.py` et le supervisor. Journaliser à chaque cycle de prod un snapshot d'entrées complet (parquet prix + hash, portfolio.json, flags, NAV) permettant de rejouer offline n'importe quel cycle passé — tout écart rejeu-vs-réel = bug détecté.
- **Points de vigilance d'implémentation (du critique)** : granularité **quotidienne** obligatoire (stops/breaker vivent dans `daily_check.py` — sinon on recrée deux surfaces de décision, la faille qu'on ferme) ; l'état d'entrée porte les plus-hauts par position et la phase de ré-entrée.
- **Prérequis** : QW-7 (non-régression) comme filet — les deux se protègent mutuellement. **Calendrier** : pendant l'étape 0-1 du plan v2, avant tout historique de prod.
- **Corpus** : cycle 5 §2.2 (NautilusTrader — emprunt d'idée, pas d'outil) ; design v2 §4 (la faille « le backtest doit simuler les stops » a déjà dû être patchée) et §2.2.
- **Effort** : semaines. **Risque** : moyen (refactor du chemin critique — d'où le calendrier et le filet).

### CM-2 — Cartographie de plateau paramétrique + PBO réellement calculé
- **Quoi** : rejouer la grille **complète pré-enregistrée** des voisins de la config de production (lookback 6-15 mois, skip 0-2, top_n 5-20, fenêtre vol 40-90 j, cible vol 10-20 %, stop 10-25 %) avec le **moteur pandas existant parallélisé** (joblib/multiprocessing — quelques heures pour ~2 000 configs sur 15 ans, une fois par re-validation). Protocole verrouillé : (1) grille figée dans un fichier versionné *avant* les runs, jamais étendue après ; (2) la config de production doit être sur un **plateau** (Sharpe des voisins > 70 % du sien ; pic isolé = rejet) ; (3) la matrice des rendements alimente enfin `probability_of_backtest_overfitting()` — le gate PBO ≤ 0,30 devient réellement calculable ; (4) chaque run incrémente `trials_registry.jsonl`. vectorbt uniquement si le temps de calcul est mesuré comme bloquant, et alors seulement pour un pré-criblage grossier sans stops, configs survivantes rejouées dans le moteur de référence — **pas de troisième implémentation de la stratégie** (contradiction avec CM-1 sinon).
- **Conséquence assumée et documentée** : le n_trials gonflé par la grille durcit le gate DSR — c'est voulu, c'est l'honnêteté.
- **Prérequis** : QW-2 (univers PIT), QW-8 (règle de comptage du registre — même fichier de protocole).
- **Corpus** : cycle 5 §1.2 ; design v2 §5 couche 7 ; rapport §1.1 ; critère de plateau : hors corpus, à vérifier.
- **Effort** : 1-2 semaines de protocole + câblage (le calcul tourne seul).

### CM-3 — Assistant de revue trimestrielle : le post-mortem McLean-Pontiff outillé
- **Quoi** : script Python d'attribution complet (contribution par position depuis le journal de fills, coûts de rotation, événements stops/breaker, Sharpe glissant vs enveloppe QW-6, taux d'erreur de la couche IA, écart yfinance/IBKR) ; Sonnet rédige un **brouillon** structuré par la checklist de décroissance post-publication, format « constat chiffré (Python) / questions à trancher par l'humain », phrase obligatoire « aucune conclusion statistique tant que n < 12 mois », **interdiction par prompt de proposer des changements de paramètres**. Diff brouillon→version validée archivé. Intégrer ici : le contrefactuel des interventions (QW-11d), le fire-drill `/ping` (QW-11e), et la ligne term spread 10Y-3M (voir CM-6).
- **Pourquoi** : la revue trimestrielle est la seule défense contre la mort lente du signal (−58 % McLean-Pontiff) ; non outillée, elle sera bâclée dès le 3e trimestre. Le script d'attribution est 80 % de la valeur, IA ou pas. Vigilance : les questions doivent rester ouvertes, pas rhétoriques (risque d'ancrage du brouillon).
- **Corpus** : rapport §2.1 ; design v2 §6, §5 couche 7, §3.2. Gardée **sans modification** par le critique.
- **Effort** : semaines (l'attribution depuis le JSONL est du vrai travail). **Coût IA** : ~0,02 $/mois amorti.

### CM-4 — CUSUM de mort du signal, en alarme (jamais en actionneur)
- **Quoi** : test CUSUM séquentiel sur l'écart entre rendement mensuel réalisé et attente dégradée (−58 %), avec page de pré-enregistrement *avant* déploiement : seuil h, ARL (~5 ans), et action au franchissement = **statut 🟠 forcé + item obligatoire du digest + revue humaine** — le pattern existant de l'ES hors enveloppe. L'humain décide, le bot ne touche à rien (le passage automatique à 50 % d'exposition initialement proposé violait le §5 couche 7 et a été retiré). Livrable clé : l'**analyse de puissance honnête** — savoir qu'il faut 3-5 ans pour détecter un signal mort est la meilleure défense contre l'abandon émotionnel à 18 mois.
- **Corpus** : rapport §2.1, §1.4 ; design v2 §6 ; CUSUM : hors corpus (Page 1954, SPC), à vérifier.
- **Effort** : le code est court ; le vrai travail est le document de pré-enregistrement. 1 semaine.

### CM-5 — Diagnostic délistés one-shot : dé-biaiser le backtest pour ~10-20 €
- **Quoi**, dans cet ordre strict : (a) prérequis QW-2 pour avoir la liste des ex-constituants ; (b) **avant tout paiement**, auditer la couverture délistés du fournisseur (Tiingo ~10 $/mois, EODHD ~20 €/mois — noms et couverture hors corpus, à vérifier) sur 10 tickers radiés connus (Lehman, Washington Mutual) via doc officielle + trial gratuit ; (c) souscrire un mois, bulk download EOD des ex-constituants, geler en parquet versionné, résilier ; (d) livrable = **diagnostic** : backtest comparatif snapshot-vs-yfinance chiffrant l'écart de Sharpe/DSR une fois pour toutes, documenté au §9.1 — pas une dépendance permanente. Attention au mapping tickers recyclés (le « AAL » pré-2013 n'est pas American Airlines). Écrire honnêtement la contrainte de licence (la plupart des ToS exigent la suppression à la résiliation — à lire, pas à présumer).
- **Pourquoi** : seule expérience qui dise si le haircut −58 % couvre ou non le survivorship (risque résiduel n°1).
- **Corpus** : design v2 §9.1 ; rapport §2.1 ; fournisseurs : hors corpus, à vérifier.
- **Effort** : 1-2 semaines. **Coût** : 10-20 € one-shot.

### CM-6 — Restitution : dashboard, tearsheets comparatifs, term spread
- **(a) Dashboard HTML statique** : extension du `tearsheet.py` existant (pas un module parallèle), régénéré au cycle mensuel et à la demande, **envoyé en pièce jointe Telegram** avec le digest post-rebalancement (pas de SSH/rclone que personne n'ouvrira). Contenu réduit au non-redondant : NAV vs enveloppe walk-forward, distance aux trailing stops, âges des composants. *(Design §6, §8 rejet du daemon ; rapport §5.4.)*
- **(b) Tearsheets QuantStats par lot** : job mensuel générant NAV paper vs SPY, vs ETF monde (exigence §4 aujourd'hui sans outil), et quant-pur vs avec-veto-shadow (la double comptabilité §3.1, journalisée mais jamais visualisée) + 3-4 chiffres de synthèse injectés au digest. Version épinglée, try/except fail-open. Gardée sans modification. *(Cycle 5 §4.1 ; design §4, §3.1.)* Effort : jours.
- **(c) Term spread 10Y-3M** : ligne dans la revue **trimestrielle** uniquement, plus une mention hebdo **au seul changement d'état** (normale→inversée ou retour), avec réserve mécanique accolée (« signal historique pré-2018 ; inversions 2019 et 2022-23 non couvertes ; aucune action prévue »). Jamais de bloc macro hebdomadaire. *(Rapport §2.4 Bauer & Mertens ; compatible rejet du RegimeFilter §8.)* Effort : heures.

### CM-7 — Fiches pédagogiques déclenchées par l'événement vécu
- **Quoi** : 5-6 fiches markdown versionnées couvrant les événements quasi certains de la première année (premier stop déclenché, premier drawdown > 8 %, premier veto sentinelle, premier mois de sous-performance vs ETF monde, première revue trimestrielle), avec citations académiques et déclencheur mécanique. Les autres fiches sont rédigées **à la première occurrence** de leur déclencheur. Une fiche maximum par rapport mensuel, en pièce jointe — jamais dans le digest hebdo (règle anti-bruit §3.2). Contextualisation courte par Sonnet, chiffres injectés.
- **Corpus** : design v2 §4 (« apprentissage instrumenté »), §3.2, §3.5 ; contenu = rapport §1.2, §7, §8bis.
- **Effort** : ~1 semaine pour les 5-6 premières. **Coût IA** : ~0,02 €/mois.

### CM-8 — Recherche diversification, vague 1 (après stabilisation, boucle recherche uniquement)
- **(a) Poche low-volatility via ETF** : allocation directe à **un** ETF min-vol (USMV en paper ; noter dès maintenant qu'un passage réel UE imposera un équivalent UCITS — contrainte PRIIPS, hors corpus, à vérifier), backtest de l'allocation 70/30 soumis au gate DSR/PBO. Le sleeve maison de 30 lignes ne se justifie que s'il bat l'ETF net de coûts en boucle recherche — charge de la preuve inversée. *(Cycle 2 §2.2, §2.1.4 ; répond au risque résiduel §9.8.)* Effort : jours + backtest.
- **(b) Residual momentum (Blitz-Huij-Martens)** : un essai au registre, régression rolling 36 mois figée à l'avance, **lag des facteurs Fama-French spécifié dans la formule (facteurs à t-2 mois, identique backtest/production)**, fallback fail-closed documenté (fetch French library en échec ⇒ cycle en 12-1 brut avec WARN). Attente reformulée : « amélioration possible mais probablement atténuée sur 500 large caps aux bêtas homogènes » — l'échec du gate est un résultat acceptable, pas une déception poussant aux variantes. *(Cycle 1 §2.3 / rapport §1.2.)* Effort : semaines.
- **(c) Tilt value 70/30 — conditionnel** : **étape 0 obligatoire** : spike de 2-3 jours vérifiant sur 10 tickers la latence, la couverture historique et la cohérence des B/P et E/P SimFin gratuits (deux claims du cycle 4 explicitement réfutées interdisent de présumer). Si le spike passe : un essai au registre, 70/30 figé sans grille, claim requalifiée « transposition, hors corpus » (un départage intra-top-20 momentum n'est pas la combinaison Asness-Moskowitz-Pedersen), critère d'abandon si SimFin casse en production (retour momentum pur automatique, fail-open). Si le spike échoue : idée close, résultat journalisé. *(Cycle 9 §B.1 ; cycle 2 §1.4 ; SimFin cycle 4.)* Effort : spike 2-3 jours, puis semaines si validé.

---

## 4. VISION LONG TERME (mois, ou dépendant de prérequis)

- **Poche satellite Europe/Japon — TSMOM pur sur ETF régionaux** : gelée jusqu'à v2 en régime de croisière avec ≥ 6 mois de paper propre (étape 7, pas une poche du build initial). Version simplifiée vers ce que le corpus valide vraiment : **TSMOM série temporelle sur 2-4 ETF régionaux larges** (Europe, Japon) — détenir si rendement propre 12-1 > 0, sinon cash — et non un classement cross-sectionnel entre 10-15 ETF pays que le corpus ne valide pas. Justification à réécrire en réponse explicite au rejet « multi-marchés » du design §8 (pourquoi la version ETF+Europe échappe aux arguments Chine/small-caps : Jacobs & Müller sur la persistance hors US, exclusion Chine maintenue). Coûts de change et commissions modélisés, gate DSR/PBO, 6 mois de paper dédiés. *(Cycle 9 §A.1, §B.1, §C.1 ; cycle 2 §1.2 ; réserve Heliyon/Huang 2020 documentée.)*
- **Sleeve low-vol maison** : uniquement si la boucle recherche démontre qu'il bat l'ETF min-vol net de coûts (cf. CM-8a).
- **Commande `/explain` interactive** : uniquement si l'usage réel de la narration mensuelle (QW-5) le justifie.
- **HRP et Black-Litterman** : entrées au registre §8 des écartés (QW-12) — HRP ré-ouvrable si > 20 positions ; BL rejeté doctrinalement, définitif.
- **Passage en argent réel** (hors périmètre actuel) : équivalents UCITS, commandes Telegram de réduction de risque (le `/pause_achats` rejeté en paper serait alors ré-évalué), revue des licences de données.

---

## 5. IDÉES REJETÉES ET POURQUOI (pour ne pas y revenir dans 6 mois)

| Idée | Raison du rejet (argument du critique) |
|---|---|
| **F-Score de Piotroski en red flag** | Justification corpus inversée : la seule claim vérifiée (Anderson et al.) est une *mise en garde* (dépendance macro ×5 en contraction), pas une validation. Taux de base quasi nul d'un F-Score ≤ 2 dans le top momentum de 500 large caps → troisième couche d'exclusion redondante, invérifiable en shadow, important SimFin en production. Le « code mort à maintenir » du rejet Lazy Prices. |
| **Sizing par semi-variance baissière** | Source (Qiao et al., prévision du VIX par REGARCH-2C) sans aucun rapport avec le sizing — justification décorative. ~25-30 observations effectives sur 60 jours = bruit doublé, poids instables. Toucherait la pièce anti-crash centrale (Barroso & Santa-Clara) pour un gain auto-noté « basse ». |
| **PEAD réouvert (variante CAR hors méga-caps)** | Aucune des deux conditions de réouverture du §8 remplie : le tercile bas du S&P 500 (15-30 Md$) n'est pas un élargissement d'univers ; l'index EDGAR donne des dates de dépôt sans horodatage avant/après clôture — fatal pour une fenêtre CAR de 3 jours. Test sous-puissant (~170 titres) = résultat ininterprétable après des mois. |
| **Annotation 8-K item 2.02 (guidance)** | Conflit frontal avec le §8 (« extraction de guidance = champ invérifiable ») : « baisse de guidance » est un jugement, pas un fait extractible — la vérification par sous-chaîne ne protège pas un booléen. Going-concern et material weakness déjà couverts par la sentinelle et les 4.02. |
| **Diff annuel des 10-K (Lazy Prices dégradé)** | Code mort assumé dès la conception (jamais branché, jamais validable). Le vrai chantier est le découpage des 10-K en sections (HTML notoirement fragile) = maintenance permanente (§9.7) pour un encart décoratif, plus invitation au surpilotage (§9.6). |
| **Moniteur 13F pédagogique** | Maximise la tentation de surpiloter (« 3 des 8 gérants ont réduit NVDA » à côté des positions du bot) sans aucune valeur décisionnelle admise. La pédagogie « qui détient quoi » s'obtient sans code (presse, WhaleWisdom). |
| **13F crowding (proxy McLean-Pontiff)** | Valeur basse avouée + effort en semaines = auto-réfutation. Chaîne causale non vérifiée, panier de gérants = degré de liberté non contrôlé → narration non falsifiable au pire moment (Sharpe hors enveloppe). Parsing CUSIP→ticker pénible et sans fin. |
| **Météo macro mensuelle (FRED + Sonnet)** | Fabrique méthodiquement l'anxiété macro qu'elle prétend encadrer ; un disclaimer mécanique n'a jamais neutralisé un chiffre affiché au-dessus. La part IA est nulle (un f-string suffit). La claim Bauer & Mertens va au blueprint pédagogique, pas au digest opérationnel. |
| **Form 4 achats d'initiés en shadow** | Reproduit trait pour trait le rejet Lazy Prices : 10 candidats/mois × 24 mois = aucune puissance, « on saura » est statistiquement faux. Littérature (Cohen-Malloy-Pomorski) hors corpus. Parsing XML/10b5-1 = maintenance permanente. |
| **XBRL companyfacts (splits + bilans)** | La confirmation de split arrive au dépôt *suivant* — systématiquement après la bataille (yfinance corporate actions est déjà la 2e source temps réel). « StockholdersEquity < 0 » crie faux sur McDonald's, Home Depot, Starbucks (rachats d'actions, pas détresse) — générateur de fausses alertes. |
| **Fenêtre de veto passif `/veto_cycle`** | Réfute un strawman (le mode observation que personne ne proposait) et ajoute en réalité un levier discrétionnaire *moins coûteux* que `/kill` — abaisser le coût de l'intervention en augmente la fréquence, l'inverse de Barber & Odean. Le cas légitime (bug de données) est couvert par `/kill` + DataSentinel. |
| **`/pause_achats` + `/reprise`** | En paper, différence cosmétique avec `/kill` pour un coût réel : troisième état bloquant dont toutes les interactions (× breaker × grâce 72 h × kill × ré-entrée) devraient être testées et backtestées. Ré-évaluable au passage en réel uniquement. |
| **NAV « fantôme » permanente** | « Le moteur de backtest sait déjà le faire » est faux : c'est un second pipeline de production temps réel à maintenir seul. Remplacée par le contrefactuel batch à la demande (QW-11d). |
| **Purge CPCV de 12 mois** | Cadre ML importé à tort (ici pas de labels chevauchants) ; purger 12 mois sur ~180 observations détruit plus de la moitié de l'échantillon — le remède vide le test. Remplacée par l'embargo 1-2 mois (QW-10d). |
| **Rejeu du momentum crash 2008-2009** | Infaisable proprement : yfinance n'a pas les radiés massifs de 2008-2009 — un stress test sur les seuls survivants produit un chiffre faux présenté comme rassurant. Remplacé par un scénario synthétique étiqueté (QW-10a). |
| **Adoption de Qlib / RD-Agent / vectorbt en prod / Grafana-Prometheus / Black-Litterman** | Rejets d'outillage confirmés : Qlib non production-ready (cycle 5), RD-Agent = IA génératrice de stratégie (violation doctrinale §3) et n_trials incontrôlable, vectorbt = troisième implémentation de la stratégie contredisant CM-1, daemon 24/7 rejeté (§8), BL exigerait des views IA (§3). Une ligne chacun au registre §8. |

---

## 6. Séquencement recommandé

> Principe : chaque phase produit un critère de validation objectif avant d'ouvrir la suivante. Les phases 0-3 s'insèrent dans le plan v2 existant (étapes 0-6, 3-4 mois) sans le retarder de plus de ~3 semaines nettes ; la diversification attend la croisière.

**Phase 0 — Fondations moteur (pendant l'étape 0-1 du plan v2, ~2-3 semaines)**
QW-7 (non-régression) → CM-1 (`decide()` + snapshot-rejeu) → QW-1 (risk-free) → QW-8 (registre v2) → QW-12 (mesures de risque).
*Validation de sortie* : test de non-régression vert ; un cycle de prod simulé rejoué offline avec écart nul ; gate re-passé avec risk-free et n_trials mécanique, run journalisé au registre.

**Phase 1 — Fondations données (~1-2 semaines, parallélisable avec la fin de la phase 0)**
QW-2 (univers PIT) → CM-5 (diagnostic délistés, dans l'ordre strict : liste → audit → achat → snapshot → diff).
*Validation de sortie* : tests unitaires des 15-20 dates charnières verts ; écart Sharpe/DSR survivants-vs-complet chiffré et documenté au §9.1.

**Phase 2 — Validation statistique complète (~2-3 semaines, exige phases 0+1)**
CM-2 (grille plateau + PBO) → QW-6 (enveloppe bootstrap) → QW-10 a-d (stress, permutation, sensibilité, chemins OOS) → CM-4 (CUSUM pré-enregistré).
*Validation de sortie* : la config de production passe le gate complet (DSR ≥ 0,90 avec n_trials honnête, PBO ≤ 0,30 réellement calculé, plateau confirmé, p < 0,10 en permutation, médiane des 21 jours au-dessus du seuil) ; `backtest_envelope.json` et le document CUSUM versionnés au tag git. **Si le gate ne passe pas : on ne déploie pas, et c'est le système qui fonctionne.**

**Phase 3 — Sentinelle et ops (~1-2 semaines, pendant les étapes 3-5 du plan v2)**
QW-3 (FTS + golden set) → QW-9 (red team) → QW-4 (intra-mois) → QW-5 (journal de décision + narration) → QW-11 a-e (earnings, préavis J-1, Telegram lecture seule, registre interventions, âges/fire-drill).
*Validation de sortie* : golden set enrichi (positifs, négatifs, SVB, synthétiques) rejoué à 100 % ; premier préavis J-1 diffusé et diffé contre le réel ; `/statut` répond avec âges.

**Phase 4 — Pilotage et revue (en continu dès le premier trimestre de paper)**
CM-3 (assistant revue trimestrielle) → CM-6 (dashboard, tearsheets, term spread) → CM-7 (fiches).
*Validation de sortie* : première revue trimestrielle réalisée avec le brouillon, diff archivé, fire-drill `/ping` effectué.

**Phase 5 — Recherche diversification (après ≥ 3-6 mois de paper propre, boucle recherche seulement)**
CM-8a (low-vol ETF) → CM-8b (residual momentum) → CM-8c (spike SimFin puis tilt value si le spike passe). Chaque candidat = essai(s) comptés au registre, promotion uniquement par le gate de la phase 2.
*Validation de sortie* : chaque candidat a un verdict journalisé — promu, ou abandonné avec résultat négatif documenté (un négatif propre est un livrable).

**Phase 6 — Long terme (v2 en croisière, ≥ 6 mois de paper)**
Poche Europe TSMOM ETF, et le reste du §4.

---

## 7. Impact budget total estimé

| Poste | Récurrent (€/mois) | One-shot (€) |
|---|---|---|
| Budget IA design v2 existant (sentinelle + digest, plafond) | ~5,00 (plafond, dépense réelle bien moindre) | — |
| Sentinelle intra-mois positions détenues (QW-4, Haiku) | +0,02 | — |
| Narration de rebalancement (QW-5, Haiku) | +0,05 | — |
| Assistant revue trimestrielle (CM-3, Sonnet, amorti) | +0,02 | — |
| Fiches pédagogiques (CM-7, Sonnet) | +0,02 | — |
| Red team golden set (QW-9, Sonnet, génération) | ~0 (rejeux amortis) | ~0,50 |
| Diagnostic délistés (CM-5, un mois de fournisseur EOD) | 0 (résilié) | 10-20 |
| EDGAR (FTS, submissions, 8-K), yfinance `^IRX`, calcul local | 0 | 0 |
| Grille paramétrique, bootstrap, permutation (CPU local/VPS existant) | 0 | 0 |
| **Total ajouts** | **≈ +0,11 €/mois** | **≈ 11-21 €** |

**Conclusion budget** : la totalité de la roadmap tient dans le plafond IA de 5 €/mois déjà arbitré par le design v2 (dépense réelle estimée < 1 €/mois tout compris), plus un investissement ponctuel de 11-21 € pour le seul chantier qui achète de la donnée — celui qui dé-biaise le backtest. Aucun abonnement récurrent nouveau, aucun service à maintenir 24/7, aucune dépendance payante en production.