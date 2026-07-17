# Rapport de recherche — Cycle 9/9 : Sources fiables Europe/Asie et benchmarks quant de référence

## Résumé exécutif

Ce dernier cycle confirme, sur la base de sources primaires peer-reviewed exclusivement, que les grandes anomalies quantitatives documentées aux États-Unis (momentum, value, momentum de série temporelle) possèdent bien des équivalents académiques rigoureux sur les marchés européens et asiatiques — répondant directement à l'angle (D) de la question de recherche. Les preuves les plus solides proviennent de quatre articles : deux études européennes sur le momentum (Heliyon 2023 ; Finance Research Letters 2017), l'article de référence mondial *Value and Momentum Everywhere* (Journal of Finance 2013, couvrant explicitement l'Europe continentale et le Japon), et une étude de réplication majeure sur le marché A-share chinois (Management Science 2024). Point notable : si le momentum et la value « voyagent » bien hors des US, l'étude chinoise montre que **la majorité (≈83%) des anomalies US ne survivent pas** sur le marché A-share sous une procédure de test fiable, nuançant fortement la transposabilité géographique des signaux quant. En revanche, les angles (A) données de bourses (Euronext, Deutsche Börse, LSE), (B) régulateurs (ESMA, AMF), (C) accès aux données asiatiques (JPX, HKEX) et (E) communautés/benchmarks (Quantpedia, SSRN, arXiv q-fin, CFA Institute) **ne sont couverts par aucun claim ayant survécu à la vérification** — ils restent à documenter (voir Limites).

---

## A. Momentum sur les marchés actions européens (équivalents non-US)

### A.1 — Momentum de série temporelle (TSM) en Europe : anomalie significative et persistante
**Confiance : haute** (source primaire académique, votes unanimes 3-0, confirmée via deux hébergements indépendants)

L'article **Vukovic, Ingenito & Maiti (2023), *Time series momentum: Evidence from the European equity market*, Heliyon 9(1):e12989** (Cell Press/Elsevier, DOI 10.1016/j.heliyon.2023.e12989, publié le 16 janvier 2023, en accès libre) documente une anomalie de momentum de série temporelle **significative et persistante** sur le marché actions européen. L'étude analyse empiriquement le TSM sur les indices actions européens (24 principaux indices) sur la période **2000-2020**, à l'aide d'un **modèle autorégressif poolé** testant le pouvoir prédictif des rendements futurs. Résultat central : les stratégies TSM permettent d'obtenir **environ 0,71% de rendement par mois au-dessus du marché** via un modèle à six facteurs. Il s'agit d'un équivalent européen direct des travaux US de Moskowitz-Ooi-Pedersen (2012).

- Sources : [ScienceDirect S2405844023001962](https://www.sciencedirect.com/science/article/pii/S2405844023001962) · [PMC9879792 (texte intégral libre)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9879792/)
- Réserve : Heliyon est un mega-journal à large spectre, peer-reviewed mais de sélectivité plus faible que les revues de finance de premier rang ; l'étude porte sur des indices (niveau pays) et non sur des actions individuelles.

### A.2 — Momentum cross-sectionnel sur 10 marchés européens : rendements affaiblis par les crises
**Confiance : haute** (source primaire peer-reviewed, votes unanimes 3-0)

L'article **« Momentum strategies in European equity markets: Perspectives on the recent financial and European debt crises », Finance Research Letters (Elsevier)** examine empiriquement les stratégies de momentum à travers **10 marchés actions européens** (Autriche, Belgique, Finlande, France, Allemagne, Irlande, Italie, Luxembourg, Pays-Bas, Espagne) sur **2003-2015**, à partir des données **Thomson Datastream**. Constats :
- Les rendements de momentum sont **plus faibles** que dans les recherches antérieures, et **statistiquement non significatifs sur 2007-2012**, attribués aux conditions de marché de la crise financière (2008-2009) et de la crise de la dette européenne (2011-2012).
- L'anomalie est **concentrée dans les small caps** : les petites capitalisations dégagent des rendements de momentum significatifs sur les deux sous-périodes, contrairement aux grandes capitalisations.

- Source : [ScienceDirect S1544612317300521](https://www.sciencedirect.com/science/article/abs/pii/S1544612317300521)
- Réserve : article sous paywall (vérification via abstract indexé) ; une divergence mineure sur la date de début (2003 vs 2004 selon les extraits) n'affecte pas le fond.

---

## B. Value et momentum « partout » : preuve globale incluant Europe et Japon

### B.1 — *Value and Momentum Everywhere* (Asness, Moskowitz, Pedersen)
**Confiance : haute** (article séminal du Journal of Finance, votes unanimes 3-0, citation vérifiée chez l'éditeur officiel)

Article de référence mondial : **Asness, C.S., Moskowitz, T.J. & Pedersen, L.H. (2013), *Value and Momentum Everywhere*, The Journal of Finance, 68(3):929-985** (DOI 10.1111/jofi.12021), revue phare peer-reviewed de l'American Finance Association. Résultats structurants pour la recherche quant multi-régions :
- Primes **value et momentum consistantes** à travers **huit marchés/classes d'actifs** diversifiés, avec une **structure de facteur commun forte** — établissant que ces anomalies ne sont pas propres aux actions US.
- Couverture **explicite des actions individuelles d'Europe continentale et du Japon** (en plus des US et du Royaume-Uni), ainsi que d'obligations, devises et matières premières : preuve documentée des anomalies value/momentum sur marchés européens **et** asiatiques.
- Value et momentum sont **négativement corrélés** entre eux, au sein et à travers les classes d'actifs, ce qui motive leur **combinaison** (bénéfice de diversification, corrélation observée jusqu'à −0,53).

- Sources : [PDF (page faculté NYU Stern / Pedersen)](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf) · corroboré par Wiley (DOI 10.1111/jofi.12021), SSRN 2174501, AQR.
- Statut : résultat fondateur, massivement cité et répliqué ; non périmé malgré la date de 2013.

---

## C. Marchés asiatiques : la plupart des anomalies US ne survivent PAS en Chine

### C.1 — Réplication des anomalies sur le marché A-share chinois
**Confiance : haute** (Management Science, revue de premier rang, votes unanimes 3-0)

Étude analogue asiatique de la littérature US « Replicating Anomalies » : **Li, Liu, Liu & Wei (2024), *Replicating and Digesting Anomalies in the Chinese A-Share Market*, Management Science 70(8):5066-5090** (INFORMS, DOI 10.1287/mnsc.2023.4904). Les auteurs répliquent **469 variables d'anomalies** similaires à celles de Hou, Xue & Zhang (2020), avec une **procédure de test fiable** (breakpoints du marché principal / mainboard, rendements pondérés par la valeur). Résultats majeurs :
- **83,37% des anomalies ne génèrent PAS de spread quintile high-minus-low significatif** en rendement brut — la plupart des anomalies documentées aux US **ne survivent pas** en Chine.
- Après ajustement du risque, le taux d'échec monte à **84,22% (alphas CAPM)** et **86,99% (alphas Fama-French 3 facteurs)**.
- La procédure conventionnelle (tous les breakpoints A-share + rendements équipondérés) est **méthodologiquement biaisée** : elle surpondère les microcaps et a une capacité d'investissement très limitée.
- Les modèles **à facteurs spécifiques à la Chine (CH3, CH4)** et le **q-factor model** sont les plus performants pour expliquer les rendements A-share sur l'échantillon complet (CH3 explique 53,85% des anomalies significatives ; CH4 : 47,44% ; q-factor : 25,64%).

- Sources : [INFORMS / Management Science (DOI 10.1287/mnsc.2023.4904)](https://pubsonline.informs.org/doi/10.1287/mnsc.2023.4904) · corroboré par RePEc/IDEAS (v70y2024i8p5066-5090) et SSRN 4365416.
- Portée : enseignement central pour l'angle (C) — la transposition mécanique de signaux US vers l'Asie est risquée ; les marchés asiatiques exigent des modèles factoriels locaux et un contrôle strict des microcaps.

---

## Synthèse pour la recherche quant Europe/Asie

| Marché | Anomalie testée | Verdict | Source (qualité) |
|---|---|---|---|
| Europe (24 indices) | TSM | Présente, ~0,71%/mois | Heliyon 2023 (peer-reviewed, mega-journal) |
| Europe (10 pays) | Momentum cross-sectionnel | Présente mais affaiblie post-2007, concentrée small caps | Finance Research Letters 2017 (peer-reviewed) |
| Europe continentale + Japon | Value & Momentum | Présentes, facteur commun global | Journal of Finance 2013 (top-tier) |
| Chine (A-share) | ~469 anomalies US | 83%+ ne survivent PAS | Management Science 2024 (top-tier) |

**Conclusion de fond :** les anomalies « canoniques » (value, momentum, TSM) sont robustes en Europe et au Japon, mais la réplication à grande échelle en Chine échoue massivement — la fiabilité d'un signal quant hors US dépend fortement du marché et de la procédure de test (pondération, breakpoints, modèle factoriel local).

---

## Limites et réserves

- **Couverture partielle de la question de recherche.** Seul l'angle (D) « recherche académique européenne/asiatique » a produit des claims vérifiés. Les angles **(A) données officielles de bourses** (Euronext, Deutsche Börse/Xetra, LSE), **(B) régulateurs** (ESMA, MiFID II transparency data, AMF), **(C) accès aux données asiatiques** (JPX/TSE, HKEX) et **(E) communautés/benchmarks** (Quantpedia, SSRN Finance, arXiv q-fin, CFA Institute) **ne sont étayés par aucun claim ayant survécu à la vérification adversariale**. Ces volets ne doivent pas être considérés comme documentés par ce cycle.
- **Accès paywall.** Plusieurs sources primaires (ScienceDirect, INFORMS) ont renvoyé des erreurs 403 à la récupération automatique ; la vérification s'est appuyée sur les abstracts indexés et des hébergements miroirs (PMC, RePEc, SSRN). Les chiffres précis (0,71% ; 83,37% ; 84,22% ; 86,99%) sont confirmés mais non lus dans le corps complet des articles.
- **Qualité inégale des revues.** *Heliyon* (angle A.1) est un mega-journal de sélectivité inférieure aux revues de finance de premier rang, contrairement à *Journal of Finance* et *Management Science*.
- **Débat sur le TSM.** Une contre-littérature notable (Huang, Li, Wang & Zhou, « Time series momentum: Is it there? », JFE 2020) conteste la robustesse statistique du TSM. Les claims A.1 restent valides tels qu'énoncés (ils rapportent le résultat d'une étude européenne donnée), mais le TSM n'est pas un fait universellement établi.
- **Sensibilité temporelle.** Les résultats de momentum européen sont datés (échantillons 2000-2020 et 2003-2015) et explicitement dépendants du régime de marché (effondrement post-2007). L'étude chinoise (2024) est récente mais porte sur un marché en évolution réglementaire rapide.

## Questions ouvertes

1. **Angles A/B/C/E non couverts :** quelles sont, factuellement, les modalités d'accès (gratuit vs payant, API, licences, délai) aux données officielles d'Euronext, Deutsche Börse, LSE, JPX et HKEX, et quelles bases publiques l'ESMA (MiFID II) et l'AMF exposent-elles réellement pour la recherche quant ? (À traiter dans un cycle complémentaire.)
2. **Benchmarks/communautés :** quel est le statut de fiabilité exact de Quantpedia, SSRN Finance Network, arXiv q-fin et de la recherche du CFA Institute (académique/curée vs commerciale) ? Aucun claim vérifié ne le documente.
3. **Généralisation asiatique :** l'échec massif des anomalies US en Chine se retrouve-t-il au Japon et à Hong Kong, ou est-il spécifique à la microstructure du marché A-share (poids des microcaps, investisseurs de détail) ?
4. **Modèles factoriels locaux :** dans quelle mesure les modèles CH3/CH4 chinois — et d'éventuels équivalents européens/japonais — devraient-ils remplacer les modèles Fama-French US comme référence dans la recherche quant régionale ?