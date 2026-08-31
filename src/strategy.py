"""Stratégies : transforment des prix en signaux.

Une stratégie ne connaît rien aux positions ni à l'argent. Elle dit
seulement « je veux être investi » (1) ou « je veux être hors marché » (0).
C'est le moteur qui traduit ça en transactions.
"""

from __future__ import annotations

import pandas as pd


class MovingAverageCross:
    """Croisement de moyennes mobiles simples.

    Long quand la MM courte passe au-dessus de la MM longue, plat sinon.
    """

    def __init__(self, fast: int = 50, slow: int = 200) -> None:
        if fast >= slow:
            raise ValueError("La moyenne courte doit être plus courte que la longue.")
        self.fast = fast
        self.slow = slow

    @property
    def name(self) -> str:
        return f"MA{self.fast}/{self.slow}"

    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:
        """Retourne une Series de 0/1 alignée sur l'index des prix.

        Attention : le signal du jour J est calculé avec la clôture du jour J.
        Il ne doit donc PAS être exécuté au prix de clôture du jour J.
        Le décalage est la responsabilité du moteur (voir engine.py).
        """
        close = prices["Close"]
        fast = close.rolling(self.fast).mean()
        slow = close.rolling(self.slow).mean()

        signal = (fast > slow).astype(int)
        # Avant d'avoir assez d'historique, pas d'opinion -> hors marché.
        signal[slow.isna()] = 0
        return signal.rename("signal")


class BuyAndHold:
    """Référence honnête. Toujours investi."""

    name = "Buy & Hold"

    def generate_signals(self, prices: pd.DataFrame) -> pd.Series:
        return pd.Series(1, index=prices.index, name="signal")
