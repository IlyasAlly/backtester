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

    # TODO semaine 1 : décider quoi faire des NaN.
    #   - Les supprimer ? Les remplir vers l'avant ?
    #   - Un ffill sur le prix de clôture est défendable, sur le volume beaucoup moins.
    #   Documentez votre choix dans le README, c'est une décision, pas un détail.
    n_nan = int(df["Close"].isna().sum())
    if n_nan:
        print(f"[avertissement] {n_nan} clôtures manquantes pour {ticker}")

    return df
