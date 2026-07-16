# Comblement des gaps prioritaires (risque) — Cycle 8/9 (très incomplet)

## Résumé exécutif

Sur les 5 sous-thèmes demandés (A: overfitting de backtest/deflated Sharpe/PBO López de Prado, B: VaR vs Expected Shortfall, C: finance comportementale/overconfidence, D: biais méthodologiques chiffrés, E: rebalancing/diversification), **seul le sous-thème D** a produit des claims ayant survécu à la vérification. Les 3 claims confirmées documentent, à partir d'une source primaire unique (Elton, Gruber & Blake, 2001, Journal of Finance), des biais chiffrés dans la base CRSP mutual funds.

## Finding

### Biais méthodologiques dans la base CRSP Mutual Fund — *Confiance : haute*
Elton, Gruber & Blake (2001, *Journal of Finance*, DOI 10.1111/0022-1082.00410) : (1) « omission bias » — données de rendement manquantes pour de nombreux fonds listés, aux caractéristiques différentes de la population générale, effet distortif équivalent au survivorship bias ; (2) rendements rapportés **biaisés à la hausse** (calcul erroné des mois avec distributions multiples le même jour), mois de fusion/disparition **inexacts dans ~50% des cas** ; (3) écarts CRSP/Morningstar concentrés sur les **données anciennes et petits fonds** (<15M$ d'actifs). Source : [Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00410).

## Limites et réserves

Cycle très incomplet : 4 des 5 axes demandés (López de Prado/deflated Sharpe/PBO ; VaR vs ES/Artzner et al. ; Barber & Odean/overconfidence, disposition effect ; rebalancing/diversification) n'ont produit **aucune claim vérifiée** — malgré un brief resserré par sujet spécifique. Seul un papier unique (Elton, Gruber & Blake 2001) couvre le sous-thème D, sans corroboration croisée avec d'autres papiers du domaine (Elton-Gruber-Blake 1996 RFS, Carhart 1997). Données empiriques datant de fin 1990s/2001 — illustration historique du phénomène, pas une évaluation de la qualité actuelle de CRSP.

## Questions ouvertes

1. Formule exacte du deflated Sharpe ratio (Bailey & López de Prado) et preuve du nombre d'essais nécessaires pour un faux signal ("Pseudo-Mathematics and Financial Charlatanism", Notices of the AMS 2014) — non couvert.
2. Démonstration formelle d'Artzner, Delbaen, Eber & Heath (1999) sur les mesures de risque cohérentes, non-subadditivité de la VaR (contre-exemples Taleb) — non couvert.
3. Impact chiffré de l'overconfidence (Barber & Odean, JoF 2000 ; QJE 2001) et disposition effect (Shefrin & Statman 1985) — non couvert.
4. Fréquence de rebalancing optimale et limites mathématiques de la diversification sur actifs corrélés — non couvert.
