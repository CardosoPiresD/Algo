# Suivi de la recherche — Bourse (boucle 8 cycles)

> Fichier de pilotage. Chaque cycle le lit au réveil pour connaître ce qui est **fait**, les **lacunes (gaps)** restantes, et cibler la suite. Mis à jour + committé à chaque cycle.

## Paramètres

- **Sujet** : la bourse — exhaustif (trading algo/quant **ET** investissement au sens large).
- **Portée** : marchés **US en priorité** ; Europe/Asie **uniquement sources triées sur le volet, les plus fiables**.
- **Crypto** : hors périmètre primaire (mentionnée seulement si transversale).
- **Langue** : français. Orientation **informative** (pas un conseil financier).
- **Cadence** : **~5 h entre cycles** (8 cycles, ~35-40 h au total). _(Ajustée le 2026-07-15 : le plafond d'usage de session — reset sur fenêtre glissante — a été atteint dès le cycle 2 avec un espacement de 15 min ; espacer à 5h laisse le quota se régénérer entre chaque cycle et évite les échecs de vérification/synthèse en cascade. Profondeur par cycle inchangée.)_
- **Livrable** : `research/RAPPORT_BOURSE.md` (cumulatif), commit/push à chaque cycle.

## Plan thématique des cycles

| Cycle | Thème | Statut |
|------:|-------|--------|
| 1 | Signaux techniques & microstructure | ✅ Fait (2026-07-15 ~01:40 UTC) |
| 2 | Signaux fondamentaux, macro & sentiment | ⏳ À faire |
| 3 | Stratégies quantitatives & littérature académique | ⏳ À faire |
| 4 | Données & flux de marché (APIs, fournisseurs) | ⏳ À faire |
| 5 | Outils, frameworks & GitHub | ⏳ À faire |
| 6 | Exécution, brokers & infrastructure | ⏳ À faire |
| 7 | Gestion du risque, bonnes pratiques & pièges | ⏳ À faire |
| 8 | Synthèse transversale & sources fiables EU/Asie + dédup finale | ⏳ À faire |

## Lacunes / gaps identifiés (à combler par les prochains cycles)

**Reliquats du cycle 1** (thème 1 non couvert intégralement par des claims vérifiés) :
- [ ] Signaux de **volatilité** : VIX/term structure, volatility clustering, régimes de volatilité → à intégrer au cycle 3 (littérature quant) ou via un focus dédié.
- [ ] Signaux de **volume** : OBV, VWAP, volume profile → à rattraper (cycle 3 ou 6/exécution pour VWAP).
- [ ] **Bid-ask spread & price impact** au sens large (au-delà de l'OFI) → cycle 6 (exécution) est le meilleur véhicule.
- [ ] **Patterns chartistes** (têtes-épaules etc., preuve scientifique — Lo, Mamaysky & Wang 2000) → cycle 3.
- [ ] **Détection de régimes** (HMM, filtres, changepoint) → cycle 3 (ML/littérature académique).
- [ ] Re-vérifier les 4 claims « unverified » du cycle 1 (détails Brock 1992, résultats Rink 2023) → opportuniste au cycle 8.
- [ ] OFI sur marchés **US** spécifiquement (Cont-Kukanov-Stoikov 2014 à sourcer directement) → cycle 3 ou 6.

## Journal des cycles

### Cycle 1 — 2026-07-15 ~01:40 UTC — Signaux techniques & microstructure
- **Volume** : 5 angles de recherche, 22 sources lues, 78 claims extraits, 25 vérifiés (3 votes contradictoires/claim) → **19 confirmés, 2 réfutés, 4 non vérifiés** (~104 agents).
- **Ajouts principaux** : (i) indicateurs techniques classiques — pouvoir prédictif historique réel (Brock-Lakonishok-LeBaron 1992) mais érodé, annulé par les coûts et le data-snooping (Park & Irwin ; Bajgrowicz & Scaillet ; Rink 2023) ; (ii) momentum cross-sectionnel et time-series = anomalie la plus robuste (Jegadeesh-Titman ; Moskowitz-Ooi-Pedersen ; survey Wiest 2023), variantes residual/risk-managed ; (iii) OFI/carnet d'ordres — fort R² explicatif court terme ; (iv) enseignements méthodo (tests hors-échantillon, Reality Check/SPA, coûts).
- **Incidents** : 1er run échoué à la synthèse (schéma JSON trop strict → corrigé en markdown libre) ; ~12 votes de vérification perdus sur limite de session (claims marqués « unverified », listés en gaps).
- **Gaps reportés** : volatilité/VIX, volume/VWAP, spread/price impact, patterns chartistes, HMM/régimes (voir section Lacunes).
