# Gestion du risque, bonnes pratiques & pièges — Cycle 7/8 (couverture partielle)

## Résumé exécutif

Ce cycle confirme trois corpus de preuve empirique/théorique robustes : (1) le volatility targeting améliore le ratio de Sharpe car la volatilité des rendements n'est pas compensée proportionnellement par un rendement espéré plus élevé (Moreira & Muir 2017 ; DeMiguel, Martín-Utrera & Uppal 2024), mais des critiques tout aussi académiques (Cederburg et al. 2020 ; Barroso & Detzel 2021) montrent que ces gains s'effondrent hors échantillon et après coûts pour la plupart des facteurs hors marché ; (2) contrairement au discours dominant selon lequel le Kelly théorique est « trop agressif », Hsieh, Barmish & Gubner (IEEE 2016) démontrent qu'il peut aussi être « trop conservateur » calculé sur données empiriques échantillonnées ; (3) l'efficacité des stop-loss est conditionnelle au régime de marché — ajoutent de la valeur en présence de momentum, nuisent en cas de retour à la moyenne (Kaminski & Lo 2014 ; Lo & Remorov 2017). **Aucune preuve vérifiée** sur VaR/CVaR, l'overfitting de backtest (Lopez de Prado), les biais look-ahead/survivorship, la finance comportementale (Barber & Odean), le rebalancing/diversification.

## Findings

### Volatility targeting — mécanisme et gains — *Confiance : haute*
Moreira & Muir (2017, JoF) et DeMiguel, Martín-Utrera & Uppal (2024, JoF) : le vol-scaling améliore le Sharpe car les variations de volatilité ne sont pas compensées proportionnellement par le rendement espéré. Pour le facteur marché US : ~4,9% d'alpha annuel, +25% de Sharpe vs buy-and-hold (Moreira & Muir). Le portefeuille conditionnel de DeMiguel et al. (2024) surperforme hors échantillon net de coûts (~16% de Sharpe vs portefeuille inconditionnel). Sources : [Moreira & Muir](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12513), [DeMiguel et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13395).

### Volatility targeting — contestation empirique — *Confiance : haute*
Cederburg, O'Doherty, Wang & Yan (2020, JFE) : les stratégies de Moreira & Muir échouent en implémentation réelle hors échantillon (instabilité des régressions de spanning). Barroso & Detzel (2021, Review of Finance) : ne survivent pas aux coûts de transaction pour la plupart des facteurs (seul le marché résiste partiellement). DeMiguel et al. (2024) prétend résoudre ces critiques via une construction conditionnelle plus sophistiquée. **Débat non tranché — ne pas présenter le vol-timing comme « prouvé efficace ».**

### Critère de Kelly — pas toujours « trop agressif » — *Confiance : haute*
Hsieh, Barmish & Gubner (IEEE 55th CDC 2016, [arXiv:1710.01786](https://arxiv.org/pdf/1710.01786)) : « Restricted Betting Theorem » — quand le Kelly est calculé sur distribution empirique échantillonnée (pas la vraie distribution) avec support non borné, il peut prescrire des paris **trop conservateurs**, nuançant la justification standard du Kelly fractionnaire.

### Stop-loss — efficacité conditionnelle au régime — *Confiance : haute*
Kaminski & Lo (2014, Journal of Financial Markets, [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=968338)) : sous marche aléatoire pure, le stop-loss diminue toujours le rendement espéré ; en présence de momentum il ajoute de la valeur, en présence de retour à la moyenne il nuit. Empiriquement (US 1950-2004) : certaines règles ajoutent 50-100 pb/mois pendant les stop-out (repli obligations), lié à un modèle à changement de régime avec « flights-to-quality ». Lo & Remorov (2017, JFM, [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418117300472)) : sur actions individuelles US, les stop-loss serrés sous-performent le buy-and-hold (coûts de transaction), sauf pour titres à forte autocorrélation sérielle — expressions analytiques closed-form dérivées.

## Limites et réserves

**Lacune majeure** : seuls 3 des 5 sous-thèmes demandés couverts (vol-scaling, Kelly, stop-loss). Non couvert : VaR/ES et critiques Taleb/Basel ; overfitting de backtest (Lopez de Prado, deflated Sharpe ratio) ; look-ahead/survivorship bias chiffré ; finance comportementale (Barber & Odean) ; rebalancing/diversification. Non trouvé plutôt qu'infirmé. Accès direct aux PDF primaires limité (403 SSRN/NBER/MIT/Wiley) — vérification par triangulation de citations secondaires convergentes. 4 claims en vote partagé (2-1).

## Questions ouvertes

1. VaR/ES : limites documentées (Taleb, Basel), preuve de supériorité de l'ES comme mesure cohérente — non couvert.
2. Overfitting de backtest : Lopez de Prado (deflated Sharpe ratio, PBO), Bailey/Borwein/Zhu — aucune claim vérifiée, à rechercher spécifiquement.
3. Biais méthodologiques : impact chiffré du survivorship bias — non trouvé (CRSP, Elton/Gruber/Blake, études de désindexation à explorer).
4. Finance comportementale (Barber & Odean) et rebalancing/diversification — totalement absents malgré leur centralité.
