# Exécution, brokers & infrastructure — Cycle 6/8 (couverture inégale)

## Résumé exécutif

Les preuves vérifiées de ce cycle couvrent solidement deux des six sous-thèmes demandés : (a) la documentation officielle des API broker US, avec un luxe de détail sur Interactive Brokers (TWS API, Web API unifiée, FIX API, limites de débit précises) et sur Tradier (limites de débit par endpoint et en-têtes HTTP de quota), et (b) un pan de la littérature académique sur les coûts d'exécution optimale, mais via un article de 2012 (Busseti & Lillo, JSTAT) qui étend un modèle d'impact de marché transitoire de type Bouchaud et al. (2004) plutôt que les papiers fondateurs eux-mêmes. **Aucune preuve n'a survécu** à la vérification pour Alpaca, pour les papiers fondateurs classiques (Almgren-Chriss 2000/2001, Kyle 1985, Perold 1988), ni pour la latence/colocation, l'architecture logicielle, et paper vs live trading.

## Findings

### API Interactive Brokers (IBKR) — *Confiance : haute*
Écosystème complet : **TWS API** (TCP socket, publish/subscribe, Python/Java/C++/C#/VB.NET/DDE, requiert TWS ou IB Gateway actif), **API Web unifiée** en consolidation (fusion Client Portal Web API + Digital Account Management + Flex Web Service, OAuth 2.0), **API FIX** (équipe dédiée), **API Excel** — accès à 100+ marchés (actions, options, futures, forex, obligations, fonds) depuis un compte unique. Depuis la v10.35.01, migration partielle vers Google Protocol Buffers. La doc officielle cible des développeurs expérimentés (OOP, sockets, multithreading), contrairement à des API REST plus légères type Alpaca. Sources : [IBKR Campus](https://www.interactivebrokers.com/campus/ibkr-api-page/ibkr-api-home/), [tws-api docs](https://interactivebrokers.github.io/tws-api/).

### Limites de débit IBKR — *Confiance : haute*
**50 messages/seconde max** client→TWS (fermeture de connexion si dépassement ; FIX API ~250 msg/s selon sources communautaires). Données historiques : pas de requêtes identiques à <15s d'intervalle, max 6 requêtes/contrat/exchange/tick-type en 2s, max 60 requêtes/fenêtre de 10 min, max 50 requêtes historiques ouvertes simultanément. Source : [tws-api docs](https://interactivebrokers.github.io/tws-api/).

### Limites de débit Tradier — *Confiance : haute*
Agrégées par jeton d'accès, fenêtres glissantes d'1 minute. Données marché/compte/ordres/watchlists : **120 req/min en production, 60 en sandbox**. Endpoints d'exécution (scope 'trade') : **60 req/min dans les deux environnements** (plus stricts en production). En-têtes HTTP dédiés pour suivi de quota temps réel (X-Ratelimit-Allowed/Used/Available/Expiry). Source : [docs.tradier.com](https://docs.tradier.com/docs/rate-limiting).

### Exécution optimale — Busseti & Lillo (2012) — *Confiance : haute*
[arXiv:1206.0682](https://arxiv.org/pdf/1206.0682) (JSTAT, DOI 10.1088/1742-5468/2012/09/P09010) : résout analytiquement et calibre sur données réelles le problème d'exécution optimale (investisseur neutre ou averse au risque), dérive une frontière efficiente coûts/risque — extension du cadre coûts/risque type Almgren-Chriss. Le modèle sous-jacent (Bouchaud et al. 2004) capture la dépendance au volume **et** la décroissance temporelle transitoire de l'impact prix, contrairement aux modèles d'impact permanent/linéaire simples type Kyle (1985). Avec coûts de spread bid-ask intégrés, la solution analytique fermée disparaît (résolution numérique requise) mais l'ajout régularise la stratégie optimale.

## Limites et réserves

Couverture très inégale : aucune preuve vérifiée pour Alpaca (API, paper trading, rate limits), ni pour les papiers fondateurs demandés (Almgren-Chriss, Kyle, Perold — la preuve obtenue est un article dérivé de 2012, pas les sources primaires). Aucun claim vérifié sur : slippage empirique large/lambda de Kyle, latence/colocation (mythe vs réalité pour petit trader), architecture logicielle (data feed, OMS, risk management), écart backtesting/paper/live trading — absence de preuve dans ce lot, pas nécessairement absence de littérature disponible. Plusieurs WebFetch directs (IBKR/Tradier/arXiv) ont échoué (403), vérification par triangulation web indépendante.

## Questions ouvertes

1. Documentation officielle d'Alpaca (endpoints REST, rate limits, paper vs live, WebSocket streaming) et comparaison formelle à IBKR/Tradier ?
2. Que disent précisément Almgren-Chriss (2000/2001), Kyle (1985) et Perold (1988) au-delà des travaux dérivés déjà trouvés ?
3. Études empiriques/institutionnelles quantifiant l'écart backtest/paper/réel pour du trading systématique non-HFT ?
4. Ressources sérieuses sur l'architecture standard d'un système de trading algo, et où la latence compte réellement pour un petit trader vs le vrai HFT ?
