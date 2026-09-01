"""Métriques de performance.

Aucune n'est difficile à coder. Elles sont toutes faciles à coder *mal* :
mauvais nombre de jours de bourse, drawdown calculé sur les rendements
au lieu de l'équité, Sharpe sans taux sans risque. Écrivez les tests.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def total_return(equity: pd.Series) -> float:
    """Rendement total sur la période, en pourcentage."""
    return (equity.iloc[-1] / equity.iloc[0] - 1) * 100


def annualized_return(equity: pd.Series) -> float:
    """CAGR en pourcentage."""

    years = len(equity) / TRADING_DAYS
    beginning = equity.iloc[0]
    ending = equity.iloc[-1]

    cagr = (ending / beginning) ** (1 / years) - 1

    return cagr * 100


def annualized_volatility(returns: pd.Series) -> float:
    """Écart-type annualisé des rendements quotidiens, en pourcentage."""

    daily_volatility = returns.std() 
    annualized_volatility = daily_volatility * np.sqrt(TRADING_DAYS) 

    return annualized_volatility * 100


def max_drawdown(equity: pd.Series) -> float:
    """Pire baisse depuis un sommet, en pourcentage (valeur négative)."""

    running_max = equity.cummax() 
    drawdown = equity / running_max - 1 
    worst_drawdown = drawdown.min() 

    return worst_drawdown * 100


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.04) -> float:
    """Sharpe annualisé."""

    daily_rf = risk_free_rate / TRADING_DAYS 
    excess_returns = returns - daily_rf 
    average_return = excess_returns.mean() 
    volatility = excess_returns.std() 
    if volatility == 0: 
        return 0.0
    
    sharpe = average_return / volatility 
    annualized_sharpe = sharpe * np.sqrt(TRADING_DAYS) 

    return annualized_sharpe


def summary(result, benchmark=None) -> pd.DataFrame:
    """Tableau récapitulatif stratégie vs référence."""
    def _row(res):
        return {
            "Rendement total (%)": round(total_return(res.equity), 2),
            "Rendement annualisé (%)": round(annualized_return(res.equity), 2),
            "Volatilité (%)": round(annualized_volatility(res.returns), 2),
            "Drawdown max (%)": round(max_drawdown(res.equity), 2),
            "Ratio de Sharpe": round(sharpe_ratio(res.returns), 2),
            "Transactions": len(res.trades),
            "Temps investi (%)": round(res.positions.mean() * 100, 1),
        }

    data = {result.strategy_name: _row(result)}
    if benchmark is not None:
        data[benchmark.strategy_name] = _row(benchmark)
    return pd.DataFrame(data)
