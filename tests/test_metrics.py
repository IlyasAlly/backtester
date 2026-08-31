"""Tests des métriques — à activer au fur et à mesure de la semaine 3."""

import numpy as np
import pandas as pd
import pytest

from src import metrics


@pytest.fixture
def equity_doublee():
    """Capital qui double sur exactement un an de bourse."""
    return pd.Series(
        np.linspace(100, 200, metrics.TRADING_DAYS),
        index=pd.date_range("2020-01-01", periods=metrics.TRADING_DAYS, freq="B"),
    )


def test_rendement_total(equity_doublee):
    assert metrics.total_return(equity_doublee) == pytest.approx(100.0)


@pytest.mark.xfail(reason="TODO semaine 3", raises=NotImplementedError)
def test_rendement_annualise(equity_doublee):
    assert metrics.annualized_return(equity_doublee) == pytest.approx(100.0, rel=0.02)


@pytest.mark.xfail(reason="TODO semaine 3", raises=NotImplementedError)
def test_drawdown_max():
    equity = pd.Series([100, 120, 90, 110])   # sommet 120, creux 90 -> -25 %
    assert metrics.max_drawdown(equity) == pytest.approx(-25.0)


@pytest.mark.xfail(reason="TODO semaine 3", raises=NotImplementedError)
def test_drawdown_nul_si_toujours_en_hausse():
    equity = pd.Series([100, 101, 102, 103])
    assert metrics.max_drawdown(equity) == pytest.approx(0.0)
