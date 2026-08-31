"""Point d'entrée en ligne de commande.

Exemple :
    python main.py --ticker AAPL --fast 50 --slow 200 --start 2015-01-01
"""

from __future__ import annotations

import argparse

from src.data import load_prices
from src.engine import run_backtest
from src.metrics import summary
from src.plotting import plot_equity
from src.strategy import BuyAndHold, MovingAverageCross


def parse_args():
    p = argparse.ArgumentParser(description="Backtesteur de croisement de moyennes mobiles.")
    p.add_argument("--ticker", default="AAPL")
    p.add_argument("--start", default="2015-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--fast", type=int, default=50)
    p.add_argument("--slow", type=int, default=200)
    p.add_argument("--capital", type=float, default=10_000.0)
    p.add_argument("--refresh", action="store_true", help="Ignorer le cache local.")
    p.add_argument("--plot", default="equity_curve.png")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    prices = load_prices(args.ticker, args.start, args.end, force_refresh=args.refresh)
    print(f"{len(prices)} séances chargées pour {args.ticker} "
          f"({prices.index[0].date()} → {prices.index[-1].date()})")

    strategy = MovingAverageCross(args.fast, args.slow)
    result = run_backtest(prices, strategy, args.capital)
    benchmark = run_backtest(prices, BuyAndHold(), args.capital)

    print()
    print(summary(result, benchmark).to_string())

    path = plot_equity(result, benchmark, ticker=args.ticker, out_path=args.plot)
    print(f"\nGraphique écrit dans {path}")


if __name__ == "__main__":
    main()
