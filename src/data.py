"""Téléchargement et mise en cache des données de marché."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"


def load_prices(
    ticker: str,
    start: str = "2015-01-01",
    end: str | None = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Retourne un DataFrame indexé par date avec les colonnes OHLCV.

    Le fichier est mis en cache sur disque : le second appel ne
    retélécharge pas. C'est ce qui rend le développement supportable
    quand on relance le script cinquante fois par jour.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{ticker.upper()}_{start}_{end or 'today'}.csv"

    if cache_path.exists() and not force_refresh:
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        return _validate(df, ticker)

    df = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,   # ajuste splits et dividendes -> évite les faux signaux
        progress=False,
    )

    if df.empty:
        raise ValueError(f"Aucune donnée retournée pour {ticker!r}. Ticker valide ?")

    # yfinance retourne parfois un MultiIndex de colonnes pour un seul ticker.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = _validate(df, ticker)
    df.to_csv(cache_path)
    return df


def _validate(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Nettoyage minimal. À enrichir : c'est ici que se cachent les bugs."""
    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes pour {ticker}: {sorted(missing)}")

    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]

    # Choix de conception : on supprime les séances incomplètes plutôt que de
    # les combler. Un ffill fabriquerait des journées à rendement nul qui
    # n'ont jamais eu lieu, ce qui réduit la volatilité mesurée et gonfle le
    # ratio de Sharpe. Mieux vaut une série plus courte qu'une série inventée.
    price_cols = ["Open", "High", "Low", "Close"]
    n_before = len(df)

    df = df.dropna(subset=price_cols)

    n_dropped = n_before - len(df)

    if n_dropped:
        print(
            f"[avertissement] {n_dropped} séances incomplètes retirées pour {ticker}"
        )

    # Le volume manquant vaut zéro : aucune transaction n'a été observée.
    # Le propager reviendrait à inventer des échanges.
    df["Volume"] = df["Volume"].fillna(0)

    if df.empty:
        raise ValueError(f"Aucune donnée valide pour {ticker}")

    return df
