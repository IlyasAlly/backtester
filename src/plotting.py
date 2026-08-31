"""Graphiques. Un seul, mais lisible."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # pas de fenêtre : on écrit un PNG
import matplotlib.pyplot as plt


def plot_equity(result, benchmark=None, ticker: str = "", out_path: str | Path = "equity_curve.png"):
    """Courbe de capital, stratégie vs référence, plus le drawdown."""
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax1.plot(result.equity.index, result.equity, label=result.strategy_name, linewidth=1.4)
    if benchmark is not None:
        ax1.plot(
            benchmark.equity.index, benchmark.equity,
            label=benchmark.strategy_name, linewidth=1.2, alpha=0.7,
        )
    ax1.set_title(f"Courbe de capital — {ticker}")
    ax1.set_ylabel("Valeur du portefeuille ($)")
    ax1.legend()
    ax1.grid(alpha=0.3)

    drawdown = (result.equity / result.equity.cummax() - 1) * 100
    ax2.fill_between(drawdown.index, drawdown, 0, alpha=0.4)
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    return out_path
