"""Tests des métriques — à activer au fur et à mesure de la semaine 3."""

import numpy as np
import pandas as pd
import pytest

from src import metrics
from src.metrics import sharpe_ratio


@pytest.fixture
def equity_doublee():
    """Capital qui double sur exactement un an de bourse."""
    return pd.Series(
        np.linspace(100, 200, metrics.TRADING_DAYS),
        index=pd.date_range("2020-01-01", periods=metrics.TRADING_DAYS, freq="B"),
    )


def test_rendement_total(equity_doublee):
    assert metrics.total_return(equity_doublee) == pytest.approx(100.0)


def test_rendement_annualise(equity_doublee):
    assert metrics.annualized_return(equity_doublee) == pytest.approx(100.0, rel=0.02)


def test_drawdown_max():
    equity = pd.Series([100, 120, 90, 110])   # sommet 120, creux 90 -> -25 %
    assert metrics.max_drawdown(equity) == pytest.approx(-25.0)


def test_drawdown_nul_si_toujours_en_hausse():
    equity = pd.Series([100, 101, 102, 103])
    assert metrics.max_drawdown(equity) == pytest.approx(0.0)


def test_sharpe_volatilite_nulle():
    """Une stratégie jamais investie produit des rendements constants.
    L'écart-type est nul : on retourne 0 plutôt que de diviser par zéro.
    """
    returns = pd.Series([0.001, 0.001, 0.001, 0.001])
    assert sharpe_ratio(returns) == 0.0

def test_sharpe_plus_volatil_donne_sharpe_inferieur():
    """À rendement moyen égal, plus de volatilité doit donner un Sharpe plus bas."""
    calme = pd.Series([0.01, 0.02, 0.01, 0.02])
    agite = pd.Series([0.00, 0.03, 0.00, 0.03])

    # Le test n'a de sens que si les moyennes sont identiques.
    assert calme.mean() == pytest.approx(agite.mean())

    assert sharpe_ratio(calme) > sharpe_ratio(agite)

