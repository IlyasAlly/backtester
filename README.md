# Backtesteur de stratégies de moyennes mobiles

Un backtesteur minimal en Python qui évalue une stratégie de croisement de
moyennes mobiles sur des données boursières quotidiennes, et la compare
systématiquement à une stratégie « acheter et conserver ».

![Courbe de capital](docs/equity_curve.png)

## Installation

```bash
git clone https://github.com/<votre-utilisateur>/backtester.git
cd backtester
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py --ticker AAPL --fast 50 --slow 200 --start 2015-01-01
```

Résultat :

```
2661 séances chargées pour AAPL (2015-01-02 → 2025-08-29)

                          MA50/200   Buy & Hold
Rendement total (%)          ...          ...
Rendement annualisé (%)      ...          ...
Volatilité (%)               ...          ...
Drawdown max (%)             ...          ...
Ratio de Sharpe              ...          ...
Transactions                 ...          ...
Temps investi (%)            ...        100.0

Graphique écrit dans equity_curve.png
```

| Option | Défaut | Description |
|---|---|---|
| `--ticker` | `AAPL` | Symbole boursier (Yahoo Finance) |
| `--start` / `--end` | `2015-01-01` / aujourd'hui | Période analysée |
| `--fast` / `--slow` | `50` / `200` | Fenêtres des moyennes mobiles |
| `--capital` | `10000` | Capital initial |
| `--refresh` | — | Ignorer le cache et retélécharger |

## Structure

```
backtester/
├── main.py              # interface en ligne de commande
├── src/
│   ├── data.py          # téléchargement, cache disque, validation
│   ├── strategy.py      # génération des signaux (0 = hors marché, 1 = investi)
│   ├── engine.py        # boucle de backtest, positions, journal des transactions
│   ├── metrics.py       # rendement, drawdown, Sharpe
│   └── plotting.py      # courbe de capital et drawdown
├── tests/               # pytest
└── data/cache/          # données téléchargées (non versionnées)
```

## Conception

**Séparation des responsabilités.** Une stratégie ne connaît que les prix et
ne produit que des signaux. Elle ignore tout des positions, du capital et des
transactions — c'est le moteur qui traduit un signal en position détenue.
Ajouter une nouvelle stratégie ne demande donc qu'une classe avec une méthode
`generate_signals`.

**Exécution décalée d'une barre.** Un signal calculé à partir de la clôture du
jour J est exécuté le jour J+1. Sans ce décalage, le backtest suppose qu'on
pouvait acheter à un prix qui n'était pas encore connu au moment de la
décision. C'est l'erreur la plus courante des backtests amateurs, et elle
produit des résultats spectaculaires et faux. Le test
`tests/test_engine.py::test_pas_de_lookahead` vérifie explicitement ce point.

**Prix ajustés.** Les données sont téléchargées avec `auto_adjust=True`, ce qui
corrige les fractionnements et les dividendes. Sans cet ajustement, un
fractionnement 4-pour-1 apparaît comme une chute de 75 % et déclenche un faux
signal de vente.

## Tests

```bash
pytest -v
```

## Limites

Ce backtesteur est un outil d'apprentissage. Les résultats qu'il produit ne
constituent ni une recommandation d'investissement ni une estimation réaliste
de rendement, pour les raisons suivantes :

- **Aucun frais de transaction ni slippage.** Chaque transaction est supposée
  s'exécuter au prix affiché, sans commission ni écart entre le prix visé et
  le prix obtenu. Sur une stratégie qui négocie souvent, cette hypothèse suffit
  à transformer une perte en gain apparent.
- **Pas de biais du survivant pris en compte.** Tester une stratégie sur un
  titre qui existe encore aujourd'hui, c'est la tester sur un gagnant connu
  d'avance.
- **Un seul titre à la fois.** Ni portefeuille, ni gestion du risque, ni
  dimensionnement des positions.
- **Positions longues uniquement**, sans effet de levier ni vente à découvert.
- **Paramètres choisis, non validés.** Les fenêtres 50/200 sont conventionnelles.
  Les optimiser sur les mêmes données que celles du test reviendrait à
  surajuster ; une validation honnête demanderait une séparation
  entraînement / test hors échantillon.
- **Données quotidiennes.** Aucune information sur ce qui se passe à
  l'intérieur d'une séance.

## Pistes d'amélioration

- Modéliser les frais et le slippage en points de base par transaction
- Séparation hors échantillon pour le choix des paramètres
- Portefeuille multi-titres avec rééquilibrage
- Stratégies supplémentaires (RSI, retour à la moyenne, momentum)

## Licence

MIT
