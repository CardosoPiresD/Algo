# Hermes — Agent de trading algorithmique (paper trading)

Agent de trading momentum basé sur la recherche approfondie du dossier
[`research/`](research/RAPPORT_BOURSE.md) (9 cycles, ~150 claims académiques
vérifiées), le design délibéré [`docs/HERMES_V2_DESIGN.md`](docs/HERMES_V2_DESIGN.md)
et la roadmap [`docs/HERMES_V2_ROADMAP.md`](docs/HERMES_V2_ROADMAP.md).
**Paper trading uniquement** — le passage en argent réel est volontairement
verrouillé (voir Sécurité).

**État v2 (Phase 0 « fondations moteur » implémentée)** : cœur de décision
unique `decide()` partagé backtest/production (stops, coupe-circuit et
ré-entrée réellement simulés ET exécutés), NAV persistante branchée sur le
coupe-circuit, taux sans risque dans le Sharpe/DSR, registre d'essais
mécanique, ES/CDaR/Ulcer, enveloppe bootstrap avec haircut −58 %, test de
non-régression sur dataset gelé, fractional shares. Reste à faire (voir
roadmap) : univers point-in-time (QW-2, CSV à construire sur ta machine),
couche ops complète, étage IA.

> ⚠️ Projet informatif/expérimental. Rien ici ne constitue un conseil en
> investissement. Les marchés comportent des risques de perte en capital.

## Stratégie

**Momentum cross-sectionnel (12-1) + filtre time-series**, univers d'actions
liquides US, rebalancing mensuel — l'anomalie la plus robuste de la littérature
académique (Jegadeesh & Titman 1993/2001 ; Moskowitz-Ooi-Pedersen 2012 ;
30 ans de confirmations hors-échantillon, voir `research/RAPPORT_BOURSE.md` §1.2).

Gestion du risque intégrée (rapport §7 + complément 8bis) :
- Pondération **inverse-volatilité** + cible de vol portefeuille (pas de levier)
- **Demi-Kelly** sur l'exposition globale
- **Trailing stops larges** (15% — les stops serrés détruisent de la valeur,
  Lo & Remorov 2017)
- **Coupe-circuit de drawdown** (15%) : trading auto-désactivé au-delà
- **Kill switch** manuel : créer un fichier `KILL_SWITCH` à la racine → aucun ordre

## Structure

```
hermes/
  config/settings.yaml     # tous les paramètres (univers, risque, broker)
  data/ingestion.py        # yfinance (backtest) + IBKR (live, avec pacing)
  strategy/momentum.py     # signal 12-1 + filtre TSMOM
  strategy/risk.py         # sizing, stops, coupe-circuit, kill switch
  backtest/engine.py       # backtest walk-forward, coûts inclus, zéro look-ahead
  backtest/validate.py     # Deflated Sharpe Ratio + PBO (López de Prado)
  execution/ibkr_client.py # client IBKR paper avec triple garde-fou
  execution/order_manager.py # ordres + journal d'audit JSONL
  reporting/tearsheet.py   # métriques + tearsheet HTML (QuantStats)
  main.py                  # CLI: backtest | paper [--dry-run]
tests/                     # 30 tests (signal, risque, backtest, sécurité)
```

## Démarrage

### 1. Installation

```bash
pip install -r requirements.txt
python -m pytest tests/    # tout doit passer
```

### 2. Backtest + validation anti-overfitting (OBLIGATOIRE avant le broker)

```bash
python -m hermes.main backtest
```

Télécharge l'historique (yfinance), lance le backtest avec coûts, puis applique
le **Deflated Sharpe Ratio** et le **PBO** (Bailey & López de Prado). Si le
verdict est `approved_for_paper: false`, **ne pas passer à l'étape suivante** —
le Sharpe observé n'est pas distinguable d'un artefact de sélection.

**Honnêteté statistique** : incrémenter `validation.n_trials` dans
`settings.yaml` à *chaque* variante de paramètres testée. Tricher ici revient à
s'auto-illusionner (voir rapport §1.4 sur le data-snooping).

### 3. Paper trading (nécessite IB Gateway/TWS sur TA machine)

1. Créer un compte paper trading chez Interactive Brokers.
2. Installer TWS ou IB Gateway, activer l'API (port paper : 7497 TWS / 4002 Gateway).
3. Vérifier `hermes/config/settings.yaml` (host/port/client_id).
4. D'abord un dry-run (calcule les ordres sans les envoyer) :

```bash
python -m hermes.main paper --dry-run
```

5. Puis le vrai cycle paper :

```bash
python -m hermes.main paper
```

5bis. Le job quotidien (NAV, trailing stops reduce-only, coupe-circuit) :

```bash
python -m hermes.main daily            # à mettre en cron quotidien (~30 s)
```

6. Automatiser (cron, rebalancing mensuel — ex. 1er jour ouvré à 15h30 UTC) :

```cron
30 15 1-3 * 1-5 cd /chemin/vers/Algo && python -m hermes.main paper >> logs/cron.log 2>&1
```

### Docker

```bash
docker build -t hermes .
docker run --network host -v $(pwd)/logs:/app/logs hermes  # dry-run par défaut
```

## Sécurité (verrous en place)

| Verrou | Effet |
|---|---|
| `account_type: paper` + vérification de port | Un port live (7496/4001) avec config paper → refus de connexion |
| Fichier `HERMES_LIVE_ACKNOWLEDGED` absent | `account_type: live` → refus de connexion |
| Fichier `KILL_SWITCH` présent | Aucun ordre n'est envoyé, tout est journalisé |
| Coupe-circuit de drawdown (15%) | Trading auto-désactivé, ordre bloqués |
| Throttling 45 msg/s | Marge sous la limite IBKR documentée (50 msg/s) |
| Journal d'audit `logs/orders.jsonl` | Chaque décision/ordre horodaté et tracé |

## Limites connues

- Le backtest yfinance ne tourne **pas** dans un environnement dont le proxy
  bloque Yahoo Finance — l'exécuter sur ta machine.
- L'univers de départ (20 tickers) est un sous-ensemble arbitraire du S&P 500 ;
  un vrai déploiement devrait utiliser les constituants historiques complets
  (attention au **survivorship bias** — rapport §4/8bis : utiliser les
  constituants point-in-time, pas la liste actuelle).
- Le momentum a des **crashes documentés** (2009, Daniel & Moskowitz) et sa
  performance US s'est affaiblie depuis ~2000 — le vol-scaling intégré atténue
  mais n'élimine pas ce risque.
- IB Gateway doit tourner en continu sur une machine que tu contrôles.
