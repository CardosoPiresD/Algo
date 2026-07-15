# Rapport de recherche approfondie — La Bourse

> **Rapport cumulatif** construit sur 8 cycles de recherche (quant/algo + investissement au sens large).
> Portée : marchés **US en priorité**, Europe/Asie via sources triées sur le volet.
> **Avertissement** : document **informatif** issu de recherches web sourcées et vérifiées — **ce n'est pas un conseil en investissement**. Les marchés comportent des risques de perte en capital.

---

## Sommaire

1. Signaux techniques & microstructure
2. Signaux fondamentaux, macro & sentiment
3. Stratégies quantitatives & littérature académique
4. Données & flux de marché (APIs, fournisseurs)
5. Outils, frameworks & GitHub
6. Exécution, brokers & infrastructure
7. Gestion du risque, bonnes pratiques & pièges
8. Synthèse transversale & sources fiables EU/Asie

---

# 1. Signaux techniques & microstructure

> **Cycle 1** — 22 sources lues, 78 affirmations extraites, 25 soumises à vérification contradictoire (3 votes/claim) → **19 confirmées, 2 réfutées, 4 non vérifiées**. Rapport brut : `cycles/cycle-01-signaux-techniques-microstructure.md`.

## Résumé exécutif

La recherche empirique de haute qualité dresse un tableau contrasté des signaux techniques : les règles techniques classiques (moyennes mobiles, breakouts de range) ont montré un pouvoir prédictif historique documenté dès Brock, Lakonishok & LeBaron (1992), mais ce pouvoir s'est érodé au fil du temps, disparaît largement une fois les coûts de transaction et le biais de data-snooping pris en compte, et ne persiste pas hors-échantillon. À l'inverse, le **momentum** — cross-sectionnel (Jegadeesh & Titman) et time-series (Moskowitz, Ooi & Pedersen) — reste l'anomalie la plus robuste et la plus généralisée de la littérature, avec 30 ans de confirmations hors-échantillon, à travers les classes d'actifs et les marchés mondiaux, avec une persistance de 1 à 12 mois suivie d'un renversement partiel à plus long horizon. Côté microstructure, l'**order flow imbalance (OFI)** construit sur le carnet d'ordres explique une part substantielle des variations de prix à très court terme (R² out-of-sample de 33 à 43 % selon l'horizon dans une étude récente). La leçon transversale de ce cycle : le tri entre signaux réels et artefacts passe par les tests hors-échantillon stricts, les corrections de data-snooping (Reality Check, SPA) et la prise en compte des coûts.

## 1.1 Indicateurs techniques classiques : preuve historique réelle, mais fragile

### La preuve fondatrice : Brock, Lakonishok & LeBaron (1992) — *Confiance : haute*

L'étude de référence teste les deux règles techniques les plus simples et populaires — **moyennes mobiles** et **trading range break** (breakouts de supports/résistances) — sur le Dow Jones sur 90 ans de données (1897–1986), en étendant l'inférence statistique standard par des techniques de **bootstrap** pour tenir compte de la non-normalité et de la volatilité variable des rendements (les modèles nuls incluent random walk, AR(1), GARCH-M, EGARCH). Source primaire : [Journal of Finance, 1992](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x).

Ce papier fonde la légitimité académique de l'analyse technique — mais ses conclusions de rentabilité ont été contestées par la suite (Sullivan, Timmermann & White 1999) sur le terrain du data-snooping, ce qui motive les sections suivantes.

### Le data-snooping : la principale raison du scepticisme académique — *Confiance : haute*

Malgré de nombreuses études rapportant des profits positifs dans une grande variété de marchés (actions, FX, futures), le scepticisme académique envers les profits du trading technique reste répandu, **principalement à cause du problème de data-snooping** (biais de tests multiples et de sur-optimisation) : [Park & Irwin (2005/2007, Journal of Economic Surveys)](https://farmdoc.illinois.edu/assets/marketing/agmas/AgMAS05_04.pdf). Ce constat est renforcé par Bajgrowicz & Scaillet (2012, JFE), qui montrent que le snooping explique l'essentiel des profits apparents des règles techniques.

### Un test « exempt de data-snooping » : les profits disparaissent — *Confiance : haute*

Park & Irwin conçoivent un test structurellement immunisé contre le snooping : ils répliquent à l'identique la procédure de Lukac, Brorsen & Irwin (1988) — règles et paramètres fixés **avant** que les nouvelles données n'existent — sur la période 1985–2003. Résultat : dans **12 marchés à terme américains** (matières premières, métaux, futures financiers), les profits techniques ont **graduellement décliné** ; les profits substantiels de 1978–1984 ne sont **plus disponibles** sur 1985–2003 ([Park & Irwin 2005, AgMAS 05-04](https://farmdoc.illinois.edu/assets/marketing/agmas/AgMAS05_04.pdf) ; version peer-reviewed : *Journal of Futures Markets*, 2010, qui ajoute les tests Reality Check et SPA et ne trouve de profits significatifs que dans 2 marchés sur 17 après correction).

### Coûts de transaction et non-persistance hors-échantillon — *Confiance : haute*

Deux résultats convergents de l'étude à grande échelle de Rink (2023, *Financial Markets and Portfolio Management* — 6 406 règles, 41 marchés, jusqu'à 66 ans, avec test SPA) :

- **Sensibilité aux coûts** : l'introduction de coûts de transaction même modérés suffit à annuler l'essentiel de la surperformance mesurée des règles techniques ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)). Corroboré par Bajgrowicz & Scaillet (2012, JFE) sur le DJIA 1897–2011 : « even in-sample, the performance is completely offset by the introduction of low transaction costs ».
- **Non-persistance** : en out-of-sample, les règles récemment les plus performantes font ensuite **significativement moins bien qu'un simple buy-and-hold** — sélectionner des règles sur leur performance passée ne fonctionne pas, ce qui jette un doute sérieux sur la possibilité de profits excédentaires réels ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)).

**Synthèse pratique (indicateurs classiques)** : les indicateurs type moyennes mobiles/breakouts ont capté une prédictibilité réelle sur données anciennes, mais celle-ci s'est érodée (cohérent avec l'hypothèse des marchés adaptatifs), disparaît sous coûts réalistes, et la sélection de règles sur backtest est structurellement piégeuse (data-snooping, tests multiples).

## 1.2 Momentum : l'anomalie la plus robuste de la littérature

### Momentum cross-sectionnel : 30 ans de confirmations — *Confiance : haute*

- Trente ans de recherche après Jegadeesh & Titman (1993) confirment que les **actions gagnantes passées continuent de surperformer les perdantes passées** ([Wiest 2023, survey FMPM](https://link.springer.com/article/10.1007/s11408-022-00417-8)).
- L'effet est **robuste à travers les classes d'actifs et les marchés mondiaux**, et constitue « peut-être la contradiction la plus généralisée de l'hypothèse d'efficience des marchés » ([Wiest 2023](https://link.springer.com/article/10.1007/s11408-022-00417-8) ; corroboré par Asness, Moskowitz & Pedersen, *Value and Momentum Everywhere*, JF 2013).
- **Test anti-snooping décisif** : les profits momentum ont persisté hors-échantillon dans les années 1990, après publication de l'étude originale, indiquant que les résultats initiaux n'étaient pas un artefact de data-snooping ([Jegadeesh & Titman 1999/2001, NBER w7159 / Journal of Finance](https://www.nber.org/system/files/working_papers/w7159/w7159.pdf)).
- **Mécanisme** : le même papier teste les modèles comportementaux (profits issus de sur-réactions retardées finissant par s'inverser) ; les résultats les **soutiennent, mais les auteurs appellent explicitement à la prudence** sur cette interprétation ([NBER w7159](https://www.nber.org/system/files/working_papers/w7159/w7159.pdf)).

### Time-series momentum : horizons, décroissance, renversement — *Confiance : haute*

Moskowitz, Ooi & Pedersen (2012, JFE), source primaire disponible via [AQR](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum) et [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463) :

- **Persistance de 1 à 12 mois** des rendements passés, puis **renversement partiel au-delà d'un an** — cohérent avec sous-réaction initiale puis sur-réaction différée. Le signal momentum décroît et se retourne à long horizon.
- Un **portefeuille diversifié de stratégies TSMOM sur toutes les classes d'actifs** produit des rendements anormaux substantiels, avec une faible exposition aux facteurs de risque standards, et **performe le mieux pendant les marchés extrêmes** (« smile » du momentum — propriété de couverture en crise, répliquée sur ~140 ans par Hurst, Ooi & Pedersen).

**Caveats obligatoires** : (a) Huang, Li, Wang & Zhou (2020, JFE, *Time series momentum: Is it there?*) contestent le canal de prédictibilité actif-par-actif (partiellement un artefact de moyennes non nulles et de volatility scaling) — le débat porte sur le mécanisme, pas sur le résultat de portefeuille ; (b) la performance out-of-sample post-2009 du trend-following a été nettement plus faible qu'en échantillon ; (c) la formulation « significatif pour chacun des 58 instruments » a été **réfutée** en vérification adversariale (0-3) — le résultat vaut au niveau portefeuille/agrégé, pas instrument par instrument.

### Variantes documentées du momentum — *Confiance : haute*

Le survey des 30 ans recense des variantes qui améliorent ou complètent le momentum cross-sectionnel classique : **time-series momentum** (Moskowitz-Ooi-Pedersen 2012), **residual momentum** (Blitz, Huij & Martens 2011 — Sharpe supérieur au momentum prix), et **risk-managed momentum** (Barroso & Santa-Clara 2015 — le scaling par volatilité élimine quasiment les *momentum crashes* documentés par Daniel & Moskowitz 2016 et double presque le Sharpe) ([Wiest 2023](https://link.springer.com/article/10.1007/s11408-022-00417-8)).

### L'« écho » de momentum de Novy-Marx : un artefact d'estimation — *Confiance : haute (position dans un débat)*

Trois résultats de Gong, Liu & Liu (2015, *Journal of Banking & Finance*, [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426614003252)) démontent le résultat de Novy-Marx (2012) selon lequel le momentum « intermédiaire » (mois t-12 à t-7) battrait le momentum récent (t-6 à t-2) :

1. Le résultat est **piloté par des biais d'estimation** : inclure les rendements des mois t-12 et t-2 gonfle le momentum intermédiaire mesuré et déflate le momentum récent sur le marché US.
2. Une fois t-12 et t-2 exclus de la construction des portefeuilles, momentum intermédiaire et récent ont un **pouvoir prédictif statistiquement indistinguable**, aux US et dans chacun de **26 marchés internationaux majeurs**.
3. Deux régularités de corrélation sérielle expliquent l'artefact : (a) **corrélation négative** entre le rendement de ce mois et celui d'il y a 2 mois (*short-term reversal*), et (b) **corrélation positive** avec le rendement d'il y a 12 mois (**saisonnalité annuelle / écho à 12 mois**, cf. Heston & Sadka 2008).

Corroboration indépendante : Goyal & Wahal (2015, JFQA) ne trouvent pas d'écho robuste dans 37 marchés hors-US. À citer comme « Gong, Liu & Liu montrent que… » (débat en cours avec Novy-Marx), mais la direction est convergente.

## 1.3 Microstructure : order flow imbalance et carnet d'ordres

### L'OFI explique les variations de prix à court terme — *Confiance : moyenne*

L'**order flow imbalance (OFI)**, construit à partir de snapshots haute fréquence du carnet d'ordres, explique les variations de prix à court terme : l'OFI standard atteint un **R² moyen out-of-sample d'environ 32,9 %, 38,1 % et 42,6 %** aux horizons de 30 secondes, 1 minute et 5 minutes sur des composantes du CSI 500 ([Su, Sun, Li & Yuan 2021, arXiv:2112.02947](https://arxiv.org/pdf/2112.02947)). Ce résultat est cohérent avec la littérature établie (Cont, Kukanov & Stoikov 2014 : R² contemporain élevé de l'OFI sur actions US).

**Caveats** : (1) preprint non peer-reviewed ; (2) l'échantillon effectif est de 10 titres sélectionnés parmi les composantes du CSI 500 ; (3) marché chinois, pas US ; (4) il s'agit d'un R² **explicatif/contemporain** (price impact), pas d'un pouvoir prédictif directement exploitable en trading — la distinction est cruciale pour éviter le piège du look-ahead.

## 1.4 Enseignements méthodologiques transversaux (pièges)

*Confiance : haute — dérivé des sources primaires ci-dessus.*

- **Data-snooping / tests multiples** : cause première des faux signaux techniques ([Park & Irwin](https://farmdoc.illinois.edu/assets/marketing/agmas/AgMAS05_04.pdf)) ; les corrections (Reality Check de White, SPA de Hansen) et surtout les **tests véritablement hors-échantillon** (règles figées avant l'existence des données) sont le gold standard.
- **Coûts de transaction** : toute évaluation de règle technique doit inclure des coûts réalistes — ils annulent typiquement la surperformance ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)).
- **Érosion post-publication** : les profits techniques déclinent au fil du temps (Park & Irwin 2005 ; cohérent avec McLean & Pontiff 2016 sur la décroissance post-publication des anomalies).
- **Sélection sur performance passée** : contre-productive — les meilleures règles récentes sous-performent ensuite le buy-and-hold ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)).
- **Le contraste momentum vs règles techniques** : le momentum a survécu au test hors-échantillon post-publication (Jegadeesh & Titman 2001), les règles techniques classiques non — c'est le critère qui sépare une anomalie réelle d'un artefact.

## 1.5 Limites de ce cycle & points à re-vérifier

- **Non couverts par des claims vérifiés** (reportés aux cycles suivants) : signaux de **volatilité** (VIX/term structure, clustering, régimes), **volume** (OBV, VWAP, volume profile), **bid-ask spread / price impact** au sens large, **patterns chartistes**, **détection de régimes (HMM, filtres)**.
- **4 claims non vérifiés** (erreurs d'infrastructure, ni confirmés ni réfutés) : détails de Brock et al. 1992 (rejet des 4 modèles nuls ; asymétrie rendement/volatilité achat/vente) et deux résultats de Rink 2023 — plausibles et cohérents, mais à re-vérifier.
- **2 claims réfutés** (transparence) : « momentum temporel significatif pour *chacun* des 58 instruments » (réfuté 0-3, vaut en agrégé seulement).
- **Sensibilité temporelle** : échantillons s'arrêtant en 2003 (Park & Irwin) / 2009 (MOP) ; performance trend-following plus faible post-2009 ; momentum US affaibli depuis fin 1990s (Bhattacharya et al. 2017), crashes documentés (2009).
- **Questions ouvertes** : base empirique des signaux VIX/HMM vs data-snooping ; OFI explicatif → prédictif net de coûts/latence sur marchés US et capacité ; exploitabilité actuelle du momentum net de coûts et tenue hors-échantillon du risk-managed momentum post-2015 ; demi-vie mesurable des signaux publiés (marchés adaptatifs).

---

# 2. Signaux fondamentaux, macro & sentiment

> **Cycle 2** — 21 sources lues, 83 affirmations extraites, 25 soumises à vérification contradictoire → **23 confirmées, 2 réfutées, 0 non vérifiée**. Rapport brut : `cycles/cycle-02-signaux-fondamentaux-macro-sentiment.md`.

## Résumé exécutif

Les preuves les plus robustes de ce cycle concernent la **dégradation post-publication des anomalies fondamentales** : sur 97 prédicteurs académiques, les rendements chutent de 26 % hors échantillon et de 58 % après publication (McLean & Pontiff, 2016), un phénomène confirmé comme **spécifiquement américain** par une méta-analyse portant sur 241 anomalies et 39 marchés (Jacobs & Müller, 2020). À l'opposé, une étude bayésienne récente (Jensen, Kelly & Pedersen, *Journal of Finance* 2023) nuance la thèse d'une « crise de réplication » : la majorité des 153 facteurs testés se répliquent, fonctionnent hors échantillon sur 93 pays et se regroupent en 13 thèmes économiques cohérents. Parmi les facteurs individuels, le **factor low-volatility/betting-against-beta** dispose d'un support empirique particulièrement solide et multi-actifs (Frazzini & Pedersen, 2014), tandis que des signaux comptables classiques comme les **accruals** (Sloan) montrent une érosion documentée liée à l'arbitrage par les hedge funds, et le **F-Score de Piotroski** s'avère fortement dépendant du régime macroéconomique. Le **PEAD** reste l'une des anomalies les plus anciennes et répliquées (50+ ans, 224 études). Ce cycle n'a en revanche produit **aucune claim vérifiée** sur les spreads de crédit, les indicateurs avancés (ISM/PMI), le sentiment des investisseurs (Baker-Wurgler), le VIX contrarian, les rapports COT, le short interest, ou les données alternatives/NLP.

## 2.1 Le « factor zoo » : robustesse, décroissance et débat sur la crise de réplication

### La décroissance post-publication des anomalies (McLean & Pontiff, 2016) — *Confiance : haute*

Sur 97 variables documentées académiquement comme prédictives des rendements cross-sectionnels d'actions, les rendements de portefeuille sont **26 % plus faibles hors échantillon** et **58 % plus faibles après publication** de l'étude ([McLean & Pontiff 2016, JoF](https://www.fmg.ac.uk/sites/default/files/2020-08/Jeffrey-Pontiff.pdf)). Les auteurs interprètent le déclin hors-échantillon (26 %) comme une **borne supérieure de l'effet de data mining**, et la différence supplémentaire (32 points) comme la part attribuable au **trading informé par la publication académique elle-même**.

La décroissance post-publication est **plus forte pour les prédicteurs ayant les rendements in-sample les plus élevés**, et les rendements résiduels persistent davantage dans les portefeuilles concentrés sur des titres à **forte volatilité idiosyncratique et faible liquidité** — cohérent avec une explication par les limites à l'arbitrage plutôt qu'une disparition pure du mispricing.

### Un phénomène essentiellement américain (Jacobs & Müller, 2020) — *Confiance : haute*

[Jacobs & Müller (2020, JFE)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19301618) étendent l'analyse à **241 anomalies dans 39 marchés actions** (2M+ observations anomalie-pays-mois). Résultat central : **les États-Unis sont le seul des 39 pays où l'on observe un déclin fiable des rendements long-short post-publication**. Les signaux fondamentaux pourraient donc conserver davantage de pouvoir prédictif hors des États-Unis après publication — un point directement pertinent pour la portée EU/Asie de ce rapport.

### Remise en question de la « crise de réplication » (Jensen, Kelly & Pedersen, 2023) — *Confiance : haute (débat actif)*

[Jensen, Kelly & Pedersen (2023, JoF)](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13249) développent un **modèle bayésien de réplication de facteurs**, opposé aux tests fréquentistes de Hou-Xue-Zhang (2020) et Harvey-Liu-Zhu (2016). Sur 153 facteurs : la majorité se répliquent, se regroupent en **13 thèmes économiques** cohérents, et fonctionnent hors échantillon sur 93 pays. Le grand nombre de facteurs observés **renforce (et n'affaiblit pas)** la preuve en faveur de chaque facteur dans ce cadre bayésien. Résultat **sensible aux choix de prior** — à présenter comme une position dans un débat actif, non un consensus.

### Critères pratiques de robustesse (Hsu & Kalesnik, Research Affiliates) — *Confiance : haute*

[Hsu & Kalesnik (2014)](https://researchaffiliates.com/en_us/publications/articles/223_finding_smart_beta_in_the_factor_zoo.html) : **value, low volatility et momentum très significatifs** ; les autres facteurs testés (dont la qualité) insignifiants dans leur cadre — *contesté* par Novy-Marx (2013) et Asness-Frazzini-Pedersen (« Quality Minus Junk »). Cinq critères de robustesse proposés : survie dans le temps, validité hors US, robustesse à la définition, explication économique crédible, **t-stat relevé à 3,5-4,0** (au lieu de 2,0) pour corriger le data-snooping — en écho direct à Harvey-Liu-Zhu.

## 2.2 Low-volatility / Betting-Against-Beta (BAB) — *Confiance : haute*

[Frazzini & Pedersen (2014, JFE)](https://www.sciencedirect.com/science/article/pii/S0304405X13002675) : relation bêta-alpha **négative** (contredit le CAPM), vérifiée sur actions US, **20 marchés internationaux, Treasuries, obligations corporate et futures** — anomalie véritablement multi-actifs. Le facteur BAB (long low-beta levier / short high-beta délevier) a réalisé un **Sharpe de 0,78 sur 1926-mars 2012**, ~2× le facteur value et +40 % vs momentum.

**Réserve** : [Novy-Marx & Velikov (2022, JFE)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21002051) montrent que ce Sharpe est gonflé par une construction non-standard (pondération quasi-égale, forte exposition micro-cap) — une version implémentable value-weighted tombe à **~0,49**, avec une part du rendement reflétant en réalité une exposition profitability/investment. Ces critiques qualifient l'implémentabilité mais **ne réfutent pas l'anomalie bêta-alpha** elle-même.

## 2.3 Signaux issus des états financiers

### Accruals (Sloan) : un signal en voie de disparition — *Confiance : haute*

[Green, Hand & Soliman (2011, Management Science)](https://pubsonline.informs.org/doi/10.1287/mnsc.1110.1320) : les rendements de la stratégie accruals (Sloan 1996) ont **décru au point de ne plus être significativement positifs** en moyenne sur les marchés US — décroissance liée à l'**augmentation du capital des hedge funds** exploitant l'anomalie, cohérent avec le cadre McLean & Pontiff.

### PEAD (Post-Earnings-Announcement Drift) — *Confiance : haute*

Dérive du cours dans la direction de la surprise de bénéfices, **contraire à l'efficience des marchés** : ajustement lent et prévisible plutôt qu'instantané. Documenté depuis **Ball & Brown (1968)**, revue de littérature synthétisant **224 études** ([Fink 2021](https://www.sciencedirect.com/science/article/pii/S2214635020303750)) — l'une des anomalies les plus répliquées de la littérature. *(Nuance : l'interprétation « mispricing pur, incompatible avec le risque » n'a pas survécu à la vérification — débat risque-vs-mispricing toujours actif.)*

### F-Score de Piotroski : dépendance forte au régime macroéconomique — *Confiance : haute*

[Anderson, Chowdhury & Uddin (2024/2025, Springer)](https://link.springer.com/article/10.1007/s11156-024-01331-y) : le F-Score **ne se comporte pas de façon stable selon les états de l'économie** — en contraction économique, les facteurs macro deviennent **~5× plus déterminants** que les facteurs propres à la firme dans la formation du score. Implication pratique : à interpréter en tenant compte du régime macro, pas comme un filtre stable en toute circonstance.

## 2.4 Signaux macro : courbe des taux — *Confiance : haute (pré-2018), à ne pas extrapoler sans réserve*

[Bauer & Mertens (2018, FRBSF)](https://www.frbsf.org/research-and-insights/publications/economic-letter/2018/03/economic-forecasts-with-yield-curve/) : **chaque récession américaine des 60 dernières années (avant 2018)** a été précédée d'une **inversion de la courbe des taux**, avec une seule fausse alerte (milieu 1960s). Corroboré indépendamment par Chicago Fed, Dallas Fed, Estrella-Mishkin. *(La formulation plus large « prédicteur remarquablement précis » n'a pas survécu à la vérification — seule la description historique précise est retenue ; les inversions 2019 et 2022-23 ne sont pas couvertes par cette source.)*

## 2.5 Limites de ce cycle & gaps

- **Non couverts par des claims vérifiés** (reportés) : **spreads de crédit**, indicateurs avancés (ISM/PMI), inflation/breakevens, **sentiment investisseurs** (Baker-Wurgler, AAII, VIX contrarian, COT, short interest, flux de fonds), **NLP/données alternatives** (Loughran-McDonald, sentiment news/earnings calls, réseaux sociaux, satellite/carte bancaire).
- **Débat méthodologique non tranché** : bayésien (Jensen-Kelly-Pedersen) vs fréquentiste (McLean-Pontiff, Jacobs-Müller) sur la réalité de la décroissance post-publication.
- **Géographie** : la décroissance post-publication semble spécifiquement américaine (Jacobs & Müller) — pertinent pour la portée EU/Asie de ce rapport, à investiguer plus avant (cycle 8).
- **2 claims réfutées** (transparence) : interprétation « PEAD = mispricing pur » (Fink) ; formulation générale « term spread = prédicteur remarquablement précis ».

---

_(Le contenu est ajouté et enrichi à chaque cycle. Voir `PROGRESS.md` pour l'avancement.)_
