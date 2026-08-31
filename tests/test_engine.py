"""Le test le plus important du projet.

Si le moteur regarde dans le futur, tout le reste ne vaut rien.
"""

import numpy as np
import pandas as pd
import pytest

from src.engine import run_backtest
from src.strategy import MovingAverageCross


@pytest.fixture
def prices():
    """Série synthétique : montée puis descente, pour que la MM croise."""
    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    values = np.concatenate([np.linspace(100, 200, 200), np.linspace(200, 120, 200)])
    return pd.DataFrame(
        {"Open": values, "High": values, "Low": values, "Close": values,
         "Volume": 1_000_000},
        index=dates,
    )


class OracleStrategy:
    """Stratégie tricheuse : elle n'est investie QUE le jour d'un grand saut.

    Si le moteur exécute correctement à J+1, cette stratégie ne doit
    capturer AUCUN gain du saut.
    """
    name = "Oracle"

    def __init__(self, jump_date):
        self.jump_date = jump_date

    def generate_signals(self, prices):
        s = pd.Series(0, index=prices.index)
        s.loc[self.jump_date] = 1
        return s


def test_pas_de_lookahead(prices):
    """Un signal du jour J ne doit pas capturer le rendement du jour J."""
    jump_date = prices.index[100]
    result = run_backtest(prices, OracleStrategy(jump_date))

    # Le jour du signal, on ne doit pas encore être investi.
    assert result.positions.loc[jump_date] == 0
    # On l'est le lendemain.
    assert result.positions.iloc[101] == 1


def test_positions_decalees_dun_jour(prices):
    strategy = MovingAverageCross(fast=5, slow=20)
    signals = strategy.generate_signals(prices)
    result = run_backtest(prices, strategy)

    pd.testing.assert_series_equal(
        result.positions,
        signals.shift(1).fillna(0).astype(int),
        check_names=False,
    )


def test_equity_part_du_capital_initial(prices):
    result = run_backtest(prices, MovingAverageCross(5, 20), initial_capital=10_000)
    assert result.equity.iloc[0] == pytest.approx(10_000)
    assert (result.equity > 0).all()


def test_hors_marche_signifie_pas_de_variation(prices):
    """Quand la position vaut 0, la valeur du portefeuille ne bouge pas."""
    result = run_backtest(prices, MovingAverageCross(5, 20))
    flat = result.positions == 0
    assert result.returns[flat].abs().max() == pytest.approx(0.0)
