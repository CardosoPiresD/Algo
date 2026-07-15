# Données & flux de marché — Cycle 4/8 (couverture très partielle)

## Résumé exécutif

Ce cycle de vérification n'a produit que des preuves solides sur deux points étroits du thème « Données & flux de marché » : (1) le positionnement de SimFin comme fournisseur de données fondamentales (profondeur historique, processus qualité, canaux d'accès) et (2) la nature et les limites de la littérature académique sur les alt-data, via l'étude qualitative de Hansen & Borch (2022, Big Data & Society). **Aucune des 6 claims confirmées ne couvre** les fournisseurs de données de marché temps réel/tick (Polygon.io, Alpha Vantage, IEX Cloud, EOD Historical Data, Nasdaq Data Link, Twelve Data, Databento), les acteurs institutionnels (Bloomberg, Refinitiv/LSEG, FactSet), SEC EDGAR, les biais de données (survivorship, point-in-time, look-ahead) ni les sources européennes/asiatiques — ces volets du brief restent non étayés et nécessitent un complément de recherche dédié.

## Findings

### SimFin — données fondamentales — *Confiance : moyenne*
Profondeur historique (20+ ans, jusqu'en 2003), processus de contrôle qualité documenté, canaux d'accès multiples (API Python, plugin Excel, bulk download CSV). Sources : [simfin.com](https://www.simfin.com/en/fundamental-data-download/), [data-quality](https://www.simfin.com/data/help/main?topic=data-quality), [GitHub](https://github.com/SimFin/simfin). *(Déclarations auto-rapportées par le fournisseur, non auditées indépendamment. Deux autres affirmations — couverture ~5000 actions US avec extension géographique planifiée, cadence de mise à jour quotidienne 24-48h — ont été RÉFUTÉES et ne sont pas reprises.)*

### Nature de la littérature académique sur les alt-data — *Confiance : haute*
Hansen & Borch (2022, Big Data & Society, [SAGE](https://journals.sagepub.com/doi/10.1177/20539517211070701)) : étude **qualitative/sociologique** (213 entretiens avec praticiens, 2014-2020), **PAS** une démonstration quantitative du pouvoir prédictif des alt-data. Introduit les concepts de « prospecting » (rendre les données exploitables) et « assetization » (transformation en actifs négociables) comme mécanismes de commercialisation. **Point méthodologique clé : cette source ne peut pas servir de preuve empirique de la valeur prédictive des alt-data** (satellite, cartes bancaires, sentiment web) — elle documente le discours et la pratique du secteur, pas une validation statistique.

## Limites et réserves

Ce lot de 6 claims vérifiées ne couvre qu'une fraction très limitée du brief de recherche du cycle 4 : aucune preuve confirmée n'a été fournie sur les fournisseurs de données de marché US, les niveaux L1/L2/L3 et tick data, les fournisseurs institutionnels, SEC EDGAR, les fournisseurs d'alt-data commerciaux (RavenPack, Thinknum), les biais de données (survivorship, point-in-time, look-ahead, corporate actions), ou les sources Europe/Asie. Ces sections nécessitent une recherche complémentaire dédiée. Sur SimFin, deux affirmations plausibles ont été explicitement réfutées — ne pas les réintroduire. L'article Hansen & Borch est rigoureux académiquement mais relève de la sociologie économique, pas de la finance quantitative — à ne pas citer comme preuve statistique.

## Questions ouvertes

1. Quelles données comparatives fiables existent sur la couverture, la latence, les niveaux (L1/L2/L3, tick) et les coûts des fournisseurs US comme Polygon.io, Databento, IEX Cloud, Alpha Vantage, Tiingo, EOD Historical Data, Nasdaq Data Link et Twelve Data ?
2. Quelles preuves peer-reviewed (au-delà de l'étude qualitative Hansen & Borch) existent sur la valeur prédictive statistiquement démontrée des alt-data en finance quantitative ?
3. Quelle documentation académique ou de praticiens sérieux traite spécifiquement du survivorship bias, du point-in-time data vs données réévaluées, et du look-ahead bias dans les bases de données fondamentales ?
4. Quelles sources publiques ou commerciales fiables couvrent les données de marché européennes (Euronext, Deutsche Börse/Xetra, LSE) et asiatiques pour la recherche quantitative ?
