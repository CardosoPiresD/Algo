# Rapport de recherche — Cycle 1/8 : Signaux techniques & microstructure de marché

## Résumé exécutif

La recherche empirique de haute qualité dresse un tableau contrasté des signaux techniques : les règles techniques classiques (moyennes mobiles, breakouts de range) ont montré un pouvoir prédictif historique documenté dès Brock, Lakonishok & LeBaron (1992), mais ce pouvoir s'est érodé au fil du temps, disparaît largement une fois les coûts de transaction et le biais de data-snooping pris en compte, et ne persiste pas hors-échantillon. À l'inverse, le **momentum** — cross-sectionnel (Jegadeesh & Titman) et time-series (Moskowitz, Ooi & Pedersen) — reste l'anomalie la plus robuste et la plus généralisée de la littérature, avec 30 ans de confirmations hors-échantillon, à travers les classes d'actifs et les marchés mondiaux, avec une persistance de 1 à 12 mois suivie d'un renversement partiel à plus long horizon. Côté microstructure, l'**order flow imbalance (OFI)** construit sur le carnet d'ordres explique une part substantielle des variations de prix à très court terme (R² out-of-sample de 33 à 43 % selon l'horizon dans une étude récente). La leçon transversale de ce cycle : le tri entre signaux réels et artefacts passe par les tests hors-échantillon stricts, les corrections de data-snooping (Reality Check, SPA) et la prise en compte des coûts.

---

## 1. Indicateurs techniques classiques : preuve historique réelle, mais fragile

### 1.1 La preuve fondatrice : Brock, Lakonishok & LeBaron (1992) — *Confiance : haute*

L'étude de référence teste les deux règles techniques les plus simples et populaires — **moyennes mobiles** et **trading range break** (breakouts de supports/résistances) — sur le Dow Jones sur 90 ans de données (1897–1986), en étendant l'inférence statistique standard par des techniques de **bootstrap** pour tenir compte de la non-normalité et de la volatilité variable des rendements (les modèles nuls incluent random walk, AR(1), GARCH-M, EGARCH). Source primaire : [Journal of Finance, 1992](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04681.x).

Ce papier fonde la légitimité académique de l'analyse technique — mais ses conclusions de rentabilité ont été contestées par la suite (Sullivan, Timmermann & White 1999) sur le terrain du data-snooping, ce qui motive les sections suivantes.

### 1.2 Le data-snooping : la principale raison du scepticisme académique — *Confiance : haute*

Malgré de nombreuses études rapportant des profits positifs dans une grande variété de marchés (actions, FX, futures), le scepticisme académique envers les profits du trading technique reste répandu, **principalement à cause du problème de data-snooping** (biais de tests multiples et de sur-optimisation) : [Park & Irwin (2005/2007, Journal of Economic Surveys)](https://farmdoc.illinois.edu/assets/marketing/agmas/AgMAS05_04.pdf). Ce constat est renforcé par Bajgrowicz & Scaillet (2012, JFE), qui montrent que le snooping explique l'essentiel des profits apparents des règles techniques.

### 1.3 Un test « exempt de data-snooping » : les profits disparaissent — *Confiance : haute*

Park & Irwin conçoivent un test structurellement immunisé contre le snooping : ils répliquent à l'identique la procédure de Lukac, Brorsen & Irwin (1988) — règles et paramètres fixés **avant** que les nouvelles données n'existent — sur la période 1985–2003. Résultat : dans **12 marchés à terme américains** (matières premières, métaux, futures financiers), les profits techniques ont **graduellement décliné** ; les profits substantiels de 1978–1984 ne sont **plus disponibles** sur 1985–2003 ([Park & Irwin 2005, AgMAS 05-04](https://farmdoc.illinois.edu/assets/marketing/agmas/AgMAS05_04.pdf) ; version peer-reviewed : *Journal of Futures Markets*, 2010, qui ajoute les tests Reality Check et SPA et ne trouve de profits significatifs que dans 2 marchés sur 17 après correction).

### 1.4 Coûts de transaction et non-persistance hors-échantillon — *Confiance : haute*

Deux résultats convergents de l'étude à grande échelle de Rink (2023, *Financial Markets and Portfolio Management* — 6 406 règles, 41 marchés, jusqu'à 66 ans, avec test SPA) :

- **Sensibilité aux coûts** : l'introduction de coûts de transaction même modérés suffit à annuler l'essentiel de la surperformance mesurée des règles techniques ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)). Corroboré par Bajgrowicz & Scaillet (2012, JFE) sur le DJIA 1897–2011 : « even in-sample, the performance is completely offset by the introduction of low transaction costs ».
- **Non-persistance** : en out-of-sample, les règles récemment les plus performantes font ensuite **significativement moins bien qu'un simple buy-and-hold** — sélectionner des règles sur leur performance passée ne fonctionne pas, ce qui jette un doute sérieux sur la possibilité de profits excédentaires réels ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)).

**Synthèse pratique (indicateurs classiques)** : les indicateurs type moyennes mobiles/breakouts ont capté une prédictibilité réelle sur données anciennes, mais celle-ci s'est érodée (cohérent avec l'hypothèse des marchés adaptatifs), disparaît sous coûts réalistes, et la sélection de règles sur backtest est structurellement piégeuse (data-snooping, tests multiples).

---

## 2. Momentum : l'anomalie la plus robuste de la littérature

### 2.1 Momentum cross-sectionnel : 30 ans de confirmations — *Confiance : haute*

- Trente ans de recherche après Jegadeesh & Titman (1993) confirment que les **actions gagnantes passées continuent de surperformer les perdantes passées** ([Wiest 2023, survey FMPM](https://link.springer.com/article/10.1007/s11408-022-00417-8)).
- L'effet est **robuste à travers les classes d'actifs et les marchés mondiaux**, et constitue « peut-être la contradiction la plus généralisée de l'hypothèse d'efficience des marchés » ([Wiest 2023](https://link.springer.com/article/10.1007/s11408-022-00417-8) ; corroboré par Asness, Moskowitz & Pedersen, *Value and Momentum Everywhere*, JF 2013).
- **Test anti-snooping décisif** : les profits momentum ont persisté hors-échantillon dans les années 1990, après publication de l'étude originale, indiquant que les résultats initiaux n'étaient pas un artefact de data-snooping ([Jegadeesh & Titman 1999/2001, NBER w7159 / Journal of Finance](https://www.nber.org/system/files/working_papers/w7159/w7159.pdf)).
- **Mécanisme** : le même papier teste les modèles comportementaux (profits issus de sur-réactions retardées finissant par s'inverser) ; les résultats les **soutiennent, mais les auteurs appellent explicitement à la prudence** sur cette interprétation ([NBER w7159](https://www.nber.org/system/files/working_papers/w7159/w7159.pdf)).

### 2.2 Time-series momentum : horizons, décroissance, renversement — *Confiance : haute*

Moskowitz, Ooi & Pedersen (2012, JFE), source primaire disponible via [AQR](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum) et [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463) :

- **Persistance de 1 à 12 mois** des rendements passés, puis **renversement partiel au-delà d'un an** — cohérent avec sous-réaction initiale puis sur-réaction différée. Le signal momentum décroît et se retourne à long horizon.
- Un **portefeuille diversifié de stratégies TSMOM sur toutes les classes d'actifs** produit des rendements anormaux substantiels, avec une faible exposition aux facteurs de risque standards, et **performe le mieux pendant les marchés extrêmes** (« smile » du momentum — propriété de couverture en crise, répliquée sur ~140 ans par Hurst, Ooi & Pedersen).

**Caveats obligatoires** : (a) Huang, Li, Wang & Zhou (2020, JFE, *Time series momentum: Is it there?*) contestent le canal de prédictibilité actif-par-actif (partiellement un artefact de moyennes non nulles et de volatility scaling) — le débat porte sur le mécanisme, pas sur le résultat de portefeuille ; (b) la performance out-of-sample post-2009 du trend-following a été nettement plus faible qu'en échantillon ; (c) la formulation « significatif pour chacun des 58 instruments » a été **réfutée** en vérification adversariale (0-3) — le résultat vaut au niveau portefeuille/agrégé, pas instrument par instrument.

### 2.3 Variantes documentées du momentum — *Confiance : haute*

Le survey des 30 ans recense des variantes qui améliorent ou complètent le momentum cross-sectionnel classique : **time-series momentum** (Moskowitz-Ooi-Pedersen 2012), **residual momentum** (Blitz, Huij & Martens 2011 — Sharpe supérieur au momentum prix), et **risk-managed momentum** (Barroso & Santa-Clara 2015 — le scaling par volatilité élimine quasiment les *momentum crashes* documentés par Daniel & Moskowitz 2016 et double presque le Sharpe) ([Wiest 2023](https://link.springer.com/article/10.1007/s11408-022-00417-8)).

### 2.4 L'« écho » de momentum de Novy-Marx : un artefact d'estimation — *Confiance : haute (mais à attribuer comme position dans un débat)*

Trois résultats de Gong, Liu & Liu (2015, *Journal of Banking & Finance*, [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426614003252)) démontent le résultat de Novy-Marx (2012) selon lequel le momentum « intermédiaire » (mois t-12 à t-7) battrait le momentum récent (t-6 à t-2) :

1. Le résultat est **piloté par des biais d'estimation** : inclure les rendements des mois t-12 et t-2 gonfle le momentum intermédiaire mesuré et déflate le momentum récent sur le marché US.
2. Une fois t-12 et t-2 exclus de la construction des portefeuilles, momentum intermédiaire et récent ont un **pouvoir prédictif statistiquement indistinguable**, aux US et dans chacun de **26 marchés internationaux majeurs**.
3. Deux régularités de corrélation sérielle expliquent l'artefact : (a) **corrélation négative** entre le rendement de ce mois et celui d'il y a 2 mois (*short-term reversal*), et (b) **corrélation positive** avec le rendement d'il y a 12 mois (**saisonnalité annuelle / écho à 12 mois**, cf. Heston & Sadka 2008).

Corroboration indépendante : Goyal & Wahal (2015, JFQA) ne trouvent pas d'écho robuste dans 37 marchés hors-US. À citer comme « Gong, Liu & Liu montrent que… » (débat en cours avec Novy-Marx), mais la direction est convergente.

---

## 3. Microstructure : order flow imbalance et carnet d'ordres

### 3.1 L'OFI explique les variations de prix à court terme — *Confiance : moyenne*

L'**order flow imbalance (OFI)**, construit à partir de snapshots haute fréquence du carnet d'ordres, explique les variations de prix à court terme : l'OFI standard atteint un **R² moyen out-of-sample d'environ 32,9 %, 38,1 % et 42,6 %** aux horizons de 30 secondes, 1 minute et 5 minutes sur des composantes du CSI 500 ([Su, Sun, Li & Yuan 2021, arXiv:2112.02947](https://arxiv.org/pdf/2112.02947)). Ce résultat est cohérent avec la littérature établie (Cont, Kukanov & Stoikov 2014 : R² contemporain élevé de l'OFI sur actions US).

**Caveats** : (1) preprint non peer-reviewed ; (2) l'échantillon effectif est de 10 titres sélectionnés parmi les composantes du CSI 500 ; (3) marché chinois, pas US ; (4) il s'agit d'un R² **explicatif/contemporain** (price impact), pas d'un pouvoir prédictif directement exploitable en trading — la distinction est cruciale pour éviter le piège du look-ahead.

---

## 4. Enseignements méthodologiques transversaux (pièges)

*Confiance : haute — dérivé des sources primaires ci-dessus.*

- **Data-snooping / tests multiples** : cause première des faux signaux techniques ([Park & Irwin](https://farmdoc.illinois.edu/assets/marketing/agmas/AgMAS05_04.pdf)) ; les corrections (Reality Check de White, SPA de Hansen) et surtout les **tests véritablement hors-échantillon** (règles figées avant l'existence des données) sont le gold standard.
- **Coûts de transaction** : toute évaluation de règle technique doit inclure des coûts réalistes — ils annulent typiquement la surperformance ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)).
- **Érosion post-publication** : les profits techniques déclinent au fil du temps (Park & Irwin 2005 ; cohérent avec McLean & Pontiff 2016 sur la décroissance post-publication des anomalies).
- **Sélection sur performance passée** : contre-productive — les meilleures règles récentes sous-performent ensuite le buy-and-hold ([Rink 2023](https://link.springer.com/article/10.1007/s11408-023-00433-2)).
- **Le contraste momentum vs règles techniques** : le momentum a survécu au test hors-échantillon post-publication (Jegadeesh & Titman 2001), les règles techniques classiques non — c'est le critère qui sépare une anomalie réelle d'un artefact.

---

## Limites et réserves

- **Couverture partielle du thème** : ce cycle n'a produit de claims vérifiés que sur (1) les indicateurs techniques classiques, (2) le momentum/mean-reversion, et (6→partiellement) les breakouts (via le *trading range break* de Brock et al.), plus l'OFI en microstructure. Les volets **volatilité (VIX, term structure, clustering)**, **volume (OBV, VWAP, volume profile)**, **bid-ask spread et price impact au sens large**, **patterns chartistes** et **détection de régimes (HMM, filtres)** ne sont **pas couverts** par des claims vérifiés et devront l'être dans des cycles ultérieurs.
- **4 claims non vérifiés** pour cause d'erreurs d'infrastructure des agents vérificateurs (ni confirmés ni réfutés) : les résultats détaillés de Brock et al. 1992 (rejet des 4 modèles nuls ; asymétrie rendement/volatilité entre signaux d'achat et de vente) et deux résultats de Rink 2023 (surperformance in-sample sous test SPA ; prédictibilité déclinant drastiquement, cohérente avec les marchés adaptatifs). Ils sont plausibles et cohérents avec les claims confirmés, mais à re-vérifier.
- **2 claims réfutés** (transparence) : la formulation « momentum temporel significatif pour **chacun** des 58 instruments » de Moskowitz-Ooi-Pedersen a été réfutée (0-3) — ne pas la reprendre ; le résultat vaut en agrégé.
- **Sensibilité temporelle** : les échantillons des études majeures s'arrêtent en 2003 (Park & Irwin), 2009 (MOP 2012) ; la performance du trend-following post-2009 a été plus faible, et les profits momentum US se sont affaiblis depuis la fin des années 1990 (Bhattacharya et al. 2017) avec des crashes documentés (2009).
- **Qualité hétérogène** : le résultat OFI repose sur un preprint arXiv (marché chinois, 10 titres) — confiance moyenne malgré la cohérence avec Cont-Kukanov-Stoikov 2014.
- **Débats de mécanisme ouverts** : Huang et al. (2020, JFE) sur le TSMOM ; Gong-Liu-Liu vs Novy-Marx sur l'écho — les claims rapportent fidèlement chaque source, mais ce sont des débats vivants.

## Questions ouvertes

1. **Signaux de volatilité et de régimes** : quelle est la base empirique des signaux VIX/term structure et des modèles HMM/filtres de détection de régimes, et souffrent-ils des mêmes problèmes de data-snooping que les règles techniques ? (À couvrir dans un cycle dédié.)
2. **OFI en prédictif** : le pouvoir *explicatif* contemporain de l'OFI se traduit-il en pouvoir *prédictif* net de coûts et de latence sur les marchés US, et à quelle échelle de capital la stratégie sature-t-elle ?
3. **Décroissance du momentum** : la décroissance post-publication (McLean & Pontiff) et les momentum crashes rendent-ils le momentum non-géré inexploitable aujourd'hui net de coûts, et le risk-managed momentum (Barroso & Santa-Clara) survit-il hors-échantillon post-2015 ?
4. **Marchés adaptatifs** : l'érosion documentée des règles techniques (Park & Irwin ; Rink) implique-t-elle une fenêtre d'exploitabilité systématique pour tout signal publié, et peut-on la mesurer (demi-vie des signaux) ?