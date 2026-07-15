# Signaux fondamentaux, macro & sentiment — Cycle 2/8 : Recherche exhaustive sur la bourse

## Résumé exécutif

Les preuves les plus robustes de ce cycle concernent la **dégradation post-publication des anomalies fondamentales** : sur 97 prédicteurs académiques, les rendements chutent de 26 % hors échantillon et de 58 % après publication (McLean & Pontiff, 2016), un phénomène confirmé comme **spécifiquement américain** par une méta-analyse portant sur 241 anomalies et 39 marchés (Jacobs & Müller, 2020). À l'opposé, une étude bayésienne récente (Jensen, Kelly & Pedersen, *Journal of Finance* 2023) nuance la thèse d'une « crise de réplication » : la majorité des 153 facteurs testés se répliquent, fonctionnent hors échantillon sur 93 pays et se regroupent en 13 thèmes économiques cohérents. Parmi les facteurs individuels, le **factor low-volatility/betting-against-beta** dispose d'un support empirique particulièrement solide et multi-actifs (Frazzini & Pedersen, 2014), tandis que des signaux comptables classiques comme les **accruals** (Sloan) montrent une érosion documentée liée à l'arbitrage par les hedge funds, et le **F-Score de Piotroski** s'avère fortement dépendant du régime macroéconomique. Le **PEAD** reste l'une des anomalies les plus anciennes et répliquées (50+ ans, 224 études). En revanche, ce cycle n'a produit **aucune claim vérifiée** sur les spreads de crédit, les indicateurs avancés (ISM/PMI), le sentiment des investisseurs (Baker-Wurgler), le VIX contrarian, les rapports COT, le short interest, ou les données alternatives/NLP — ces sous-thèmes restent à documenter.

---

## 1. Le « factor zoo » : robustesse, décroissance et débat sur la crise de réplication

### 1.1 La décroissance post-publication des anomalies (McLean & Pontiff, 2016)

**Confiance : haute** (source primaire unique mais peer-reviewed *Journal of Finance*, votes unanimes, résultat largement cité et répliqué).

Sur 97 variables documentées académiquement comme prédictives des rendements cross-sectionnels d'actions, les rendements de portefeuille sont **26 % plus faibles hors échantillon** et **58 % plus faibles après publication** de l'étude ([McLean & Pontiff 2016, JoF](https://www.fmg.ac.uk/sites/default/files/2020-08/Jeffrey-Pontiff.pdf)). Les auteurs interprètent le déclin hors-échantillon (26 %) comme une **borne supérieure de l'effet de data mining**, et la différence supplémentaire (32 points, soit 58 %-26 %) comme la part attribuable au **trading informé par la publication académique elle-même** — c'est-à-dire qu'environ un tiers de l'alpha initial disparaît spécifiquement parce que le signal devient public et exploité.

Point important pour la robustesse du signal : la décroissance post-publication est **plus forte pour les prédicteurs ayant les rendements in-sample les plus élevés**, et les rendements résiduels persistent davantage dans les portefeuilles concentrés sur des titres à **forte volatilité idiosyncratique et faible liquidité** — cohérent avec une explication par les limites à l'arbitrage (coûts de transaction, risque idiosyncratique) plutôt qu'une disparition pure du mispricing.

### 1.2 Un phénomène essentiellement américain (Jacobs & Müller, 2020)

**Confiance : haute** (source primaire, *Journal of Financial Economics*, plus grande méta-analyse internationale du sujet).

[Jacobs & Müller (2020, JFE)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X19301618) étendent l'analyse à **241 anomalies cross-sectionnelles dans 39 marchés actions**, sur plus de deux millions d'observations anomalie-pays-mois. Résultat central : **les États-Unis sont le seul des 39 pays où l'on observe un déclin fiable des rendements long-short post-publication**. Aucun des 38 marchés internationaux ne présente de déclin statistiquement significatif. Autrement dit, la décroissance post-publication documentée par McLean & Pontiff apparaît comme un **phénomène essentiellement américain**, possiblement lié à une arbitrage plus efficace et un accès plus large au capital spéculatif aux États-Unis — ce qui implique que les signaux fondamentaux (value, profitability, accruals, etc.) pourraient conserver davantage de pouvoir prédictif hors des États-Unis après publication.

### 1.3 Remise en question de la « crise de réplication » (Jensen, Kelly & Pedersen, 2023)

**Confiance : haute** (Journal of Finance, méthodologie bayésienne novatrice ; débat académique actif à signaler).

[Jensen, Kelly & Pedersen (2023, JoF)](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13249) développent un **modèle bayésien de réplication de facteurs** — alternative aux tests fréquentistes facteur par facteur utilisés par des études plus pessimistes (Hou-Xue-Zhang 2020 ; Harvey-Liu-Zhu 2016). Leurs conclusions, sur 153 facteurs :
- La **majorité des facteurs peuvent être répliqués** ;
- Ils se **regroupent en 13 thèmes économiques** (value, quality, low risk, investment, momentum, accruals, etc.), et la majorité de ces thèmes contribuent significativement au portefeuille de tangence — le factor zoo se réduit donc à un nombre restreint de dimensions réellement distinctes ;
- Les facteurs **fonctionnent hors échantillon sur un jeu de données couvrant 93 pays** ;
- Le grand nombre de facteurs observés **renforce (et n'affaiblit pas)** la preuve en faveur de chaque facteur, car dans le cadre bayésien les facteurs corrélés s'informent mutuellement — un contrepoint direct aux critiques de multiple testing.

Ce résultat est **sensible aux choix de prior** et le débat avec Harvey-Liu-Zhu / Hou-Xue-Zhang reste ouvert ; il doit être présenté comme la position de cette étude, non comme un consensus définitif.

### 1.4 Critères pratiques de robustesse et « survivants » du factor zoo (Hsu & Kalesnik, Research Affiliates)

**Confiance : haute** (source primaire quant reconnue, corroborée par mirrors indépendants).

[Hsu & Kalesnik (2014, Research Affiliates)](https://researchaffiliates.com/en_us/publications/articles/223_finding_smart_beta_in_the_factor_zoo.html) testent value, momentum, low volatility, quality et size sur données US et internationales, avec définitions multiples. Résultat : **value, low volatility et momentum sont très significatifs** ; le marché et l'illiquidité sont significatifs ; **les autres facteurs proposés — y compris diverses définitions de la qualité — sont statistiquement insignifiants** dans leur test (ce résultat sur la qualité est contesté par d'autres travaux peer-reviewed, notamment Novy-Marx 2013 et Asness-Frazzini-Pedersen « Quality Minus Junk », et doit être présenté avec cette réserve).

Les auteurs proposent **cinq critères de robustesse hors-échantillon** pour juger un facteur : (1) survie dans le temps, (2) validité hors des États-Unis, (3) robustesse aux variations mineures de définition, (4) explication économique crédible, (5) t-stat élevé pour corriger le data-snooping. En écho à Harvey-Liu-Zhu, ils recommandent de **relever le seuil de significativité d'un t-stat de 2,0 à 3,5 (idéalement 4,0)** pour compenser la prolifération de facteurs et les biais de publication.

---

## 2. Low-volatility / Betting-Against-Beta (BAB)

**Confiance : haute** (source primaire *Journal of Financial Economics*, résultat parmi les plus répliqués de la littérature ; caveats importants d'une critique peer-reviewed récente).

[Frazzini & Pedersen (2014, JFE)](https://www.sciencedirect.com/science/article/pii/S0304405X13002675) documentent que les actifs à bêta élevé délivrent des rendements ajustés du risque (alpha) **plus faibles** que les actifs à bêta faible — une relation bêta-alpha négative qui contredit le CAPM standard (« security market line » plate). Ce résultat se vérifie non seulement sur les actions américaines mais aussi sur **20 marchés actions internationaux, les bons du Trésor, les obligations corporate et les contrats futures** — ce qui en fait une anomalie fondamentale véritablement multi-actifs.

Un facteur long-short **Betting Against Beta (BAB)** — long en actifs à faible bêta (levier appliqué) et short en actifs à bêta élevé (déleviérage appliqué) — produit des **rendements ajustés du risque positifs et statistiquement significatifs** après contrôle des facteurs standards. Pour les actions américaines, ce facteur a réalisé un **Sharpe ratio de 0,78 sur 1926-mars 2012**, soit environ **deux fois celui du facteur value** et **40 % de plus que le momentum** sur la même période.

**Réserve importante** : [Novy-Marx & Velikov (2022, JFE), « Betting Against Betting Against Beta »](https://www.sciencedirect.com/science/article/abs/pii/S0304405X21002051) montrent que ce Sharpe de 0,78 est gonflé par une construction non-standard (pondération quasi égale, forte exposition micro-cap, méthode de shrinkage du bêta) : une version value-weighted, implémentable, ramène le Sharpe à ~0,49, et une bonne part du rendement net de coûts reflète en réalité une exposition aux facteurs profitability/investment plutôt qu'à l'anomalie bêta elle-même. Ces critiques qualifient la mécanique et l'implémentabilité, mais **ne réfutent pas l'existence de l'anomalie bêta-alpha négative** documentée empiriquement dans l'article original.

---

## 3. Signaux issus des états financiers

### 3.1 Accruals (Sloan) : un signal en voie de disparition

**Confiance : haute** (Management Science, peer-reviewed, corroboré par la littérature de décroissance générale).

[Green, Hand & Soliman (2011, Management Science)](https://pubsonline.informs.org/doi/10.1287/mnsc.1110.1320) montrent que les rendements de la stratégie hedge long-short fondée sur l'anomalie des accruals (Sloan 1996) ont **décru sur les marchés actions américains au point de ne plus être, en moyenne, significativement positifs** — un cas documenté et mesurable de décroissance post-publication d'un signal comptable classique. Ce déclin s'explique en partie par l'**augmentation du capital investi par les hedge funds** pour l'exploiter, mesurée directement via les actifs sous gestion des hedge funds et le volume de transactions sur les titres à accruals extrêmes — un mécanisme d'arbitrage qui érode les anomalies une fois publiées, cohérent avec le cadre général de McLean & Pontiff (section 1.1).

### 3.2 PEAD (Post-Earnings-Announcement Drift)

**Confiance : haute** (revue de littérature peer-reviewed synthétisant 224 études, résultat fondateur répliqué depuis 1968).

Le PEAD désigne la **dérive du cours d'une action dans la direction de la surprise de bénéfices** pendant une période prolongée après l'annonce : contrairement à l'hypothèse d'efficience des marchés, une surprise de bénéfices n'entraîne **pas** un ajustement complet et instantané des prix, mais une **dérive lente et prévisible** ([Fink 2021, Journal of Behavioral and Experimental Finance](https://www.sciencedirect.com/science/article/pii/S2214635020303750)). Le phénomène est documenté depuis plus de 50 ans (première mise en évidence par **Ball & Brown, 1968**), et la revue de Fink synthétise **216 articles publiés plus 8 working papers** — ce qui en fait l'une des anomalies les plus étudiées et répliquées de la littérature financière académique.

*(Note : une claim sur l'interprétation « mispricing pur, incompatible avec les explications par le risque » proposée par Fink n'a pas survécu à la vérification adversariale et n'est donc pas reprise ici comme fait établi — le débat risque-vs-mispricing sur le PEAD reste actif dans la littérature.)*

### 3.3 F-Score de Piotroski : dépendance forte au régime macroéconomique

**Confiance : haute** (Review of Quantitative Finance and Accounting, 2024/2025, peer-reviewed).

Une étude récente ([Anderson, Chowdhury & Uddin, 2024/2025, Springer](https://link.springer.com/article/10.1007/s11156-024-01331-y)) montre que le F-Score de Piotroski **ne se comporte pas de manière stable selon les états de l'économie** : contrairement à l'usage courant qui le traite comme un signal invariant, les conditions macroéconomiques affectent fortement le F-Score agrégé, et l'effet de chaque composante individuelle varie substantiellement selon la phase du cycle économique. Plus précisément, **pendant les épisodes de contraction économique, les facteurs monétaires et macroéconomiques deviennent nettement plus déterminants que les facteurs propres à la firme** dans la formation des valeurs du F-Score (les auteurs chiffrent l'importance des variables macro à environ cinq fois supérieure en contraction qu'en expansion). Implication pratique : un signal fondamental « pur » comme le F-Score doit être interprété en tenant compte du régime macro, pas comme un filtre stable en toutes circonstances.

---

## 4. Signaux macro : courbe des taux

**Confiance : haute pour la description historique pré-2018 ; ne pas extrapoler sans réserve à la période post-2018.**

[Bauer & Mertens (2018, FRBSF Economic Letter)](https://www.frbsf.org/research-and-insights/publications/economic-letter/2018/03/economic-forecasts-with-yield-curve/) documentent que **chaque récession américaine des 60 dernières années (avant 2018)** a été précédée d'une **inversion de la courbe des taux** (term spread négatif), et qu'une inversion a **toujours** été suivie d'un ralentissement économique — avec une **seule fausse alerte** (inversion non suivie de récession officielle, milieu des années 1960, généralement attribuée au stimulus budgétaire de l'époque). Ce constat est corroboré indépendamment par d'autres publications de la Fed (Chicago Fed, Dallas Fed, Estrella-Mishkin) sur la même série de récessions (1960, 1969-70, 1973-75, 1980, 1981-82, 1990-91, 2001, 2007-09).

*(Une claim caractérisant plus largement le term spread comme un « prédicteur remarquablement précis » n'a pas survécu à la vérification et n'est donc pas retenue comme fait établi indépendant — seule la description historique précise ci-dessus est confirmée.)*

---

## Limites et réserves

- **Couverture incomplète du périmètre demandé** : ce cycle devait couvrir cinq blocs (facteurs académiques, signaux comptables, macro, sentiment/positionnement, news/NLP/données alternatives). Seuls les trois premiers blocs disposent de claims vérifiées avec succès. **Aucune claim n'a survécu** sur : spreads de crédit, indicateurs avancés (ISM/PMI), inflation/breakevens, sentiment des investisseurs (Baker & Wurgler), put/call ratio, VIX contrarian, AAII/Investors Intelligence, COT reports, short interest, flux de fonds, sentiment NLP des news/earnings calls (Loughran-McDonald), réseaux sociaux, ou données alternatives (satellite, carte bancaire, web scraping). Ces sous-thèmes restent à traiter dans un cycle ultérieur ou une recherche complémentaire.
- **Débat non tranché sur la « crise de réplication »** : Jensen, Kelly & Pedersen (2023) et McLean & Pontiff (2016)/Jacobs & Müller (2020) présentent des lectures en tension — la première nuance fortement la décroissance post-publication via une méthodologie bayésienne sensible aux priors ; les secondes documentent un déclin robuste (au moins aux États-Unis) avec une méthodologie fréquentiste. Les deux approches sont peer-reviewed et de haut niveau ; le lecteur doit garder à l'esprit qu'il s'agit d'un débat méthodologique actif, non d'un consensus.
- **BAB/low-volatility** : le Sharpe ratio de 0,78 rapporté par Frazzini & Pedersen (2014) est une statistique de portefeuille théorique ; Novy-Marx & Velikov (2022) montrent qu'une version implémentable, nette de coûts, tombe à ~0,49 et reflète en partie une exposition à d'autres facteurs (profitability, investment).
- **Facteur qualité contesté** : la conclusion de Hsu & Kalesnik (2014) selon laquelle les définitions de la qualité seraient statistiquement insignifiantes est en désaccord avec d'autres travaux peer-reviewed reconnus (Novy-Marx 2013 ; Asness-Frazzini-Pedersen). Ne pas traiter comme un fait établi.
- **PEAD — explication mispricing vs risque** : la claim initiale attribuant à Fink (2021) la conclusion que le PEAD est incompatible avec les explications fondées sur le risque n'a pas été retenue après vérification adversariale (vote 1-2) ; le débat risque/mispricing reste ouvert dans la littérature académique.
- **Sensibilité temporelle** : la relation courbe des taux/récession est bornée « avant 2018 » dans la source citée ; les épisodes d'inversion 2019 et 2022-2023 (récession retardée ou absente à ce jour) ne sont pas couverts par cette claim et nécessiteraient une source plus récente pour être intégrés sans distorsion.
- **Géographie** : plusieurs résultats (décroissance post-publication, notamment) sont spécifiquement américains ; leur validité hors des États-Unis est soit non confirmée, soit inversée (cas Jacobs & Müller montrant l'absence de déclin dans 38 marchés internationaux).

## Questions ouvertes

1. Le débat bayésien (Jensen-Kelly-Pedersen) vs fréquentiste (McLean-Pontiff, Jacobs-Müller) sur la réalité et l'ampleur de la décroissance post-publication des facteurs sera-t-il tranché par de futurs travaux, et quelle méthodologie devrait primer pour un usage pratique en gestion quantitative ?
2. Dans quelle mesure le F-Score de Piotroski (et d'autres scores composites comptables) devraient-ils être **conditionnés au régime macroéconomique** en pratique — existe-t-il des versions « macro-ajustées » validées empiriquement ?
3. Quel est l'état de la recherche sur les signaux de sentiment (Baker-Wurgler, VIX contrarian, AAII, COT, short interest) et les données alternatives/NLP (Loughran-McDonald, RavenPack, réseaux sociaux) — leur pouvoir prédictif réel a-t-il été établi par des études peer-reviewed comparables en rigueur à celles couvertes ici ? (à traiter dans un cycle complémentaire)
4. Les spreads de crédit et les indicateurs avancés (ISM/PMI, breakevens d'inflation) offrent-ils un pouvoir prédictif indépendant de celui de la courbe des taux, ou sont-ils largement redondants avec elle comme signal de régime macro ?