# Outils, frameworks & bibliothèques open-source pour le trading algorithmique et la recherche quantitative

## Résumé exécutif

L'écosystème open-source du trading algorithmique et de la recherche quantitative en Python est mature mais hétérogène en termes de maintenance réelle. Parmi les frameworks de backtesting, **zipline-reloaded** (fork communautaire post-Quantopian) et **vectorbt** (avec sa déclinaison commerciale PRO) sont activement maintenus, tandis que **bt** reste explicitement qualifié de stade « alpha » par son propre auteur malgré une activité de développement continue ; **backtrader** n'a pas pu être confirmé comme actif (ses métriques de popularité ont été réfutées lors de la vérification). Côté plateformes complètes, **QuantConnect/LEAN** (moteur C# avec API Python) et **NautilusTrader** (moteur natif Rust avec parité recherche-production) se distinguent par une popularité GitHub élevée et une cadence de développement soutenue et vérifiable ; **freqtrade** confirme sa nature open-source GPL-3.0 et son module ML intégré FreqAI, mais ses chiffres de popularité annoncés n'ont pas résisté à la vérification. Pour la recherche quant orientée ML, **Qlib** (Microsoft) se démarque par la richesse de son pipeline (apprentissage supervisé, RL, et le nouvel agent LLM autonome RD-Agent). Enfin, **Riskfolio-Lib** et **QuantStats** couvrent respectivement l'optimisation de portefeuille (26+ mesures de risque convexes, CVXPY) et l'analyse de performance (stats/plots/reports), avec une maintenance et une adoption confirmées pour Riskfolio-Lib.

---

## 1. Frameworks de backtesting Python

### 1.1 Zipline-reloaded — successeur maintenu de Quantopian zipline
**Confiance : haute** (source primaire unique mais vérifiée en profondeur, vote 3-0)

Zipline-reloaded est le fork communautaire de la bibliothèque zipline de Quantopian, maintenu par Stefan Jansen depuis la fermeture de Quantopian fin 2020. Le dépôt affiche **1,8k stars** et **6 694 commits** sur la branche principale, avec des commits récents (dernier commit constaté le 13 novembre 2025, correction de dépendances) et plusieurs contributeurs actifs (stefan-jansen, dependabot, gnzsnz, fstp, realfishsam, lhjnilsson). Le projet est notamment utilisé comme socle pédagogique dans le livre *Machine Learning for Algorithmic Trading* de Stefan Jansen.
Source : [github.com/stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded)

*Note : une affirmation selon laquelle la dernière release stable serait la v3.1.1 du 23 juillet 2025 n'a **pas** résisté à la vérification (0-3) et doit être considérée comme non fiable.*

### 1.2 vectorbt / VectorBT PRO — backtesting vectorisé haute performance
**Confiance : haute** (source primaire GitHub, vérifiée à plusieurs reprises, votes 3-0)

Le dépôt `polakowo/vectorbt` totalise environ **8 300 stars**, **1 100 forks** et **121 issues ouvertes**, signe d'une adoption large mais d'un backlog de maintenance non négligeable. Le projet reste activement développé : la dernière release (v1.1.0) date du **5 juillet 2026** (ajout du support Python 3.14/pandas 3 et d'un moteur Rust optionnel), le dépôt comptabilise **1 077 commits** sur `master`, et un commit a été observé daté du **14 juillet 2026** — soit la veille de la date de référence de ce rapport — confirmant une activité continue au-delà même de la dernière release.

Point structurant pour les chercheurs quant : la version open-source **vectorbt** est explicitement positionnée comme l'**édition communautaire gratuite** d'un produit commercial distinct, **VectorBT PRO** (vectorbt.pro). Selon les discussions des mainteneurs, la version OSS continuera de recevoir des correctifs et le support de nouvelles versions Python, mais les **nouvelles fonctionnalités majeures sont désormais orientées vers la version PRO** ou vers des contributions communautaires via pull requests — un arbitrage important à connaître avant d'investir dans l'écosystème gratuit.
Sources : [github.com/polakowo/vectorbt](https://github.com/polakowo/vectorbt), [github.com/polakowo/vectorbt/releases](https://github.com/polakowo/vectorbt/releases)

### 1.3 Backtesting.py — API simple orientée exécution rapide
**Confiance : haute** (source primaire, vote 3-0)

Backtesting.py se positionne (auto-description du projet) comme offrant une **API simple et bien documentée**, une **exécution rapide** (« blazing fast execution »), un **optimiseur intégré**, une **bibliothèque de stratégies de base et utilitaires réutilisables/composables**, et fonctionne avec **tout instrument financier disposant de données en chandeliers (candlestick)**.
Source : [github.com/kernc/backtesting.py](https://github.com/kernc/backtesting.py)

*Note : les chiffres précis avancés ailleurs (8,7k stars, 1,5k forks, 434 commits) n'ont **pas** été confirmés (1-2) et ne doivent pas être considérés comme fiables sans re-vérification directe.*

### 1.4 bt — framework arborescent construit sur ffn
**Confiance : haute** (source primaire, deux vérifications indépendantes convergentes, votes 3-0)

`bt` (pmorissette/bt) est un framework de backtesting open-source structuré autour d'une **architecture arborescente (tree structure)** et de **piles d'algorithmes modulaires (Algos / AlgoStacks)**, facilitant la composition de stratégies complexes et réutilisables. Il est explicitement **construit sur la bibliothèque `ffn`** (fonctions financières pour Python).

Le projet montre une activité réelle — **656 commits** sur `master`, **11 releases** (confirmées croisées via l'API PyPI), la dernière (**v1.2.0**) datée du **25 avril 2026**, avec une mise à jour de branche observée le 3 juillet 2026 — mais son propre README le qualifie toujours explicitement de **« stade alpha »** (« bt is currently in alpha stage »), un signal de prudence à transmettre aux utilisateurs envisageant une mise en production.
Source : [github.com/pmorissette/bt](https://github.com/pmorissette/bt)

---

## 2. Plateformes de recherche/trading algorithmique complètes

### 2.1 QuantConnect / LEAN — moteur event-driven C# avec API Python
**Confiance : haute** (source primaire, corroboration secondaire, votes 3-0)

LEAN est le moteur de trading algorithmique open-source **event-driven** développé par QuantConnect, avec **20,5k stars** et **5k forks** sur GitHub — une popularité en croissance organique constatée (un instantané antérieur d'environ un mois montrait 19,9k/4,9k). Le dépôt est composé à **94,2 % de C#** contre seulement **5,6 % de Python**, ce qui signifie que **le moteur sous-jacent est écrit en C#**, même si l'API utilisateur (« writing algorithms ») est disponible en Python via une interopérabilité Python.Net (« LEAN uses Python.Net to bridge between your Python code and the underlying C# engine », selon la documentation officielle QuantConnect). Ce point est important pour évaluer les performances, la maintenabilité et la contribution au projet pour un utilisateur venant du monde Python pur.
Source : [github.com/QuantConnect/Lean](https://github.com/QuantConnect/Lean)

### 2.2 NautilusTrader — moteur natif Rust, parité recherche/production
**Confiance : haute** (source primaire, corroboration tierce, votes 3-0)

NautilusTrader est un moteur de trading open-source **natif Rust**, à architecture **event-driven déterministe**, conçu pour permettre d'utiliser le **même code entre backtesting et trading live** (« research-to-production parity », « strategies deploy from research to production with no code changes »), avec un « plan de contrôle » (control plane) en Python pour la logique de stratégie, la configuration et l'orchestration. Le projet affiche **24,7k stars**, **3,2k forks** et **78 issues ouvertes**, avec une cadence de développement très soutenue (environ 30 commits sur une fenêtre de 3 jours fin juin 2026, dernière release « 1.230.0 » le 29 juin 2026). Des sources tierces (discussions Hacker News, articles dev.to) corroborent la description sans la contredire, tout en signalant des réserves d'adoption réelles : projet encore sujet à des changements cassants, complexité de build Rust/Cython, licence LGPL-3.0 à examiner, compétences Rust/Python requises.
Source : [github.com/nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)

### 2.3 Freqtrade — bot crypto open-source avec module ML natif (FreqAI)
**Confiance : haute** pour la nature/licence/fonctionnalités (votes 3-0) ; **popularité non confirmée**

Freqtrade est un bot de trading cryptomonnaie **gratuit et open-source, écrit en Python**, sous licence **GPL-3.0** (confirmée directement via le fichier LICENSE du dépôt). Il intègre nativement des capacités de **machine learning via son module FreqAI**, destiné à la modélisation prédictive adaptative (« self-trains to the market via adaptive machine learning methods »), aux côtés d'un moteur de **backtesting** intégré et d'une **optimisation de stratégie par hyperopt**. Ces trois fonctionnalités (FreqAI, backtesting, hyperopt) sont confirmées comme réellement natives (non des add-ons tiers), y compris via un article évalué par les pairs (JOSS) décrivant FreqAI.
Sources : [github.com/freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) (README, LICENSE)

*Note : l'affirmation de 52,3k stars / 10,9k forks n'a **pas** été confirmée (0-3) — la popularité réelle du dépôt doit être re-vérifiée indépendamment avant citation.*

---

## 3. Bibliothèques ML/quant spécialisées

### 3.1 Qlib (Microsoft) — plateforme d'investissement quant orientée IA
**Confiance : haute** (source primaire, votes 3-0)

Qlib est une **plateforme d'investissement quantitatif open-source développée par Microsoft** (licence MIT), orientée IA, se présentant comme couvrant **tout le pipeline de recherche quant** — de l'exploration d'idées à la mise en production (traitement des données, entraînement de modèles, backtesting, découverte d'alpha, évaluation de risque, optimisation de portefeuille, exécution). Le dépôt totalise **46,3k stars** et **2 065 commits**, avec une dernière release (v0.9.7) datée d'août 2025.

Qlib supporte plusieurs **paradigmes de modélisation ML** : apprentissage supervisé, modélisation de la dynamique de marché, et **apprentissage par renforcement**. Il intègre désormais **RD-Agent**, un framework d'agents autonomes basé sur des LLM (« LLM-Based Autonomous Evolving Agents for Industrial Data-Driven R&D ») destiné à automatiser la recherche de facteurs et l'optimisation conjointe des modèles — une fonctionnalité récente documentée aussi dans un article arXiv dédié (« R&D-Agent-Quant »).
Sources : [github.com/microsoft/qlib](https://github.com/microsoft/qlib), [github.com/microsoft/RD-Agent](https://github.com/microsoft/RD-Agent)

*Réserve d'usage rapportée par des utilisateurs (non contredisant la description factuelle) : outil non considéré comme « production-ready » pour le trading live par certains retours, et courbe d'apprentissage élevée.*

### 3.2 Riskfolio-Lib — optimisation de portefeuille avancée
**Confiance : haute** (source primaire + corroboration croisée readthedocs/PyPI, votes 3-0)

Riskfolio-Lib a accumulé **4,4k stars** et **685 forks** sur GitHub, un niveau d'adoption notable dans la niche spécifique de l'optimisation de portefeuille en Python (à comparer, à titre indicatif, aux ~5,3k stars de PyPortfolioOpt, sans que cette dernière n'ait été vérifiée dans ce cycle).

La bibliothèque implémente **plus de 26 mesures de risque convexes** réparties en trois catégories (dispersion, downside, drawdown), ainsi que le **clustering hiérarchique (HRP/HERC)**, la **Nested Clustered Optimization (NCO)**, et l'intégration du **modèle Black-Litterman** (y compris variantes bayésienne et augmentée). Elle est **construite sur CVXPY** pour l'optimisation convexe, s'intègre étroitement avec **Pandas**, et requiert **Python 3.10 ou supérieur**.
Sources : [github.com/dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib), documentation readthedocs, PyPI

---

## 4. Métriques de performance

### 4.1 QuantStats — analyse de performance de portefeuille en trois modules
**Confiance : haute** (source primaire, vote 3-0)

QuantStats structure l'analyse de performance de portefeuille en **trois modules distincts** : `quantstats.stats` (calcul de métriques comme le Sharpe ratio, la volatilité, le win rate), `quantstats.plots` (visualisation des drawdowns et statistiques glissantes), et `quantstats.reports` (génération de tearsheets et rapports par lot au format HTML). Cette architecture modulaire en fait un outil fréquemment cité dans les comparatifs quant pour la restitution de métriques de performance.
Source : [github.com/ranaroussi/quantstats](https://github.com/ranaroussi/quantstats)

*Note : les chiffres précis de popularité (7,4k stars, 1,2k forks) et la date de release v0.0.81 n'ont **pas** été confirmés (1-2) et sont à re-vérifier avant citation.*

---

## Limites et réserves

- **Couverture incomplète du périmètre demandé** : ce cycle de vérification n'a produit aucune claim confirmée (3-0) sur plusieurs outils explicitement demandés — **backtrader** (les chiffres avancés ont été réfutés), **TA-Lib, pandas-ta, tsfresh** (analyse technique/features), **mlfinlab/Hudson & Thames, PyPortfolioOpt, empyrical** (les chiffres QuantStats concurrents n'ont pas non plus été confirmés), **pandas, polars, scikit-learn, PyTorch/TensorFlow**, et **awesome-quant / communautés (r/algotrading, forums Quantopian archivés)**. L'absence de claims confirmées ne signifie pas que ces outils sont moins pertinents — elle reflète les limites du processus de vérification pour ce cycle, pas une évaluation négative de ces projets.
- **Sensibilité temporelle forte** : la quasi-totalité des métriques citées (stars, forks, commits, dates de release) sont des instantanés au **15 juillet 2026** et évoluent en continu — notamment pour des projets aussi actifs que vectorbt (commit la veille de la date de référence) ou NautilusTrader (~30 commits sur 3 jours). Ces chiffres doivent être re-vérifiés pour tout usage différé.
- **Chiffres de popularité contradictoires/réfutés** : plusieurs affirmations quantitatives soumises au même processus de vérification ont été **explicitement réfutées** (backtrader : 22,5k stars/5,2k forks et 2 404 commits/63 PR ouvertes ; zipline-reloaded : release v3.1.1 du 23/07/2025 ; Backtesting.py : 8,7k stars/1,5k forks/434 commits ; freqtrade : 52,3k stars/10,9k forks ; QuantStats : 7,4k stars/1,2k forks/v0.0.81) — signe que les statistiques GitHub en cache ou via recherche web peuvent être obsolètes ou erronées, et qu'une vérification directe sur la page du dépôt reste nécessaire avant toute publication.
- **Un seul type de source dominant** : toutes les claims confirmées reposent sur des **sources primaires GitHub** (README, pages de dépôt, releases) plutôt que sur des comparatifs indépendants tiers (QuantStart, Hudson & Thames, Alpha Architect) demandés dans la requête initiale — aucun de ces comparatifs n'a produit de claim ayant survécu au vote 3-0 dans ce cycle.
- **« Alpha stage » et statut de maturité** : `bt` reste officiellement en stade alpha malgré une activité de commits soutenue — un signal à ne pas minimiser pour un usage en production.
- **Structure freemium non détaillée** : la ligne de démarcation exacte des fonctionnalités entre vectorbt (OSS) et VectorBT PRO (commercial) n'est connue que via les discussions des mainteneurs et n'a pas fait l'objet d'un audit fonctionnel détaillé feature-par-feature.

## Questions ouvertes

1. Quel est l'état réel de maintenance de **backtrader** (mementum/backtrader), un des frameworks historiquement les plus cités, alors que ses métriques n'ont pas résisté à la vérification dans ce cycle — le projet est-il toujours actif ou en déclin ?
2. Quelle est la maturité réelle et la comparaison factuelle (stars, contributeurs, cadence de commits) de **TA-Lib, pandas-ta, tsfresh, mlfinlab (Hudson & Thames), PyPortfolioOpt et empyrical**, qui n'ont pu être documentés dans ce cycle faute de claims ayant survécu au vote adversarial ?
3. Dans quelle mesure la liste communautaire **awesome-quant** reste-t-elle à jour et fiable comme point d'entrée de référence, et comment se positionnent les forums/communautés historiques (Quantopian archivé, communauté QuantConnect, r/algotrading) en termes d'utilité réelle pour un chercheur quant en 2026 ?
4. Quel est l'écart de performance et de fonctionnalités réellement mesurable entre **vectorbt (OSS)** et **VectorBT PRO**, au-delà des annonces des mainteneurs — un audit comparatif indépendant serait utile pour trancher l'arbitrage coût/bénéfice pour un chercheur individuel.