"""Le moteur de backtest.

Règle unique et non négociable : on n'agit jamais sur une information
qu'on n'avait pas encore. Le signal calculé avec la clôture du jour J
est exécuté à l'ouverture du jour J+1.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    equity: pd.Series          # valeur du portefeuille, base 1.0
    positions: pd.Series       # 0/1 par jour, position réellement détenue
    returns: pd.Series         # rendements quotidiens de la stratégie
    trades: pd.DataFrame       # journal des entrées/sorties
    strategy_name: str


def run_backtest(prices: pd.DataFrame, strategy, initial_capital: float = 10_000.0):
    """Exécute la stratégie sur les prix et retourne un BacktestResult."""
    signals = strategy.generate_signals(prices)

    # ---- LE DÉCALAGE. Toute la validité du backtest tient dans cette ligne.
    positions = signals.shift(1).fillna(0).astype(int)

    # TODO semaine 2 : rendements de l'actif puis de la stratégie.
    #   asset_returns = prices["Close"].pct_change().fillna(0.0)
    #   strat_returns = positions * asset_returns
    #   equity = (1 + strat_returns).cumprod() * initial_capital
    asset_returns = prices["Close"].pct_change().fillna(0.0)
    strat_returns = (positions * asset_returns).rename("returns")
    equity = ((1 + strat_returns).cumprod() * initial_capital).rename("equity")

    trades = _extract_trades(positions, prices["Close"])

    return BacktestResult(
        equity=equity,
        positions=positions,
        returns=strat_returns,
        trades=trades,
        strategy_name=getattr(strategy, "name", strategy.__class__.__name__),
    )


def _extract_trades(positions: pd.Series, close: pd.Series) -> pd.DataFrame:
    """Journal des transactions : une ligne par aller-retour."""
    changes = positions.diff().fillna(positions.iloc[0])
    entries = positions.index[changes == 1]
    exits = positions.index[changes == -1]

    rows = []
    for entry in entries:
        later = exits[exits > entry]
        exit_date = later[0] if len(later) else positions.index[-1]
        entry_px = float(close.loc[entry])
        exit_px = float(close.loc[exit_date])
        rows.append(
            {
                "entry_date": entry,
                "exit_date": exit_date,
                "entry_price": entry_px,
                "exit_price": exit_px,
                "return_pct": (exit_px / entry_px - 1) * 100,
                "days_held": (exit_date - entry).days,
                "still_open": exit_date == positions.index[-1] and len(later) == 0,
            }
        )
    return pd.DataFrame(rows)
