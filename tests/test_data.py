import pandas as pd
import pytest

from src.data import _validate


@pytest.fixture
def df_avec_trous():
    """Séance incomplète le 3 janvier, volume manquant le 2 janvier."""
    return pd.DataFrame(
        {
            "Open": [100, 101, None, 103, 104],
            "High": [105, 106, None, 108, 109],
            "Low": [95, 96, None, 98, 99],
            "Close": [100, 101, None, 103, 104],
            "Volume": [1000, None, 1200, 1300, 1400],
        },
        index=pd.date_range("2025-01-01", periods=5),
    )


def test_seance_incomplete_supprimee(df_avec_trous):
    result = _validate(df_avec_trous, "TEST")
    assert pd.Timestamp("2025-01-03") not in result.index
    assert len(result) == 4


def test_seances_valides_conservees(df_avec_trous):
    result = _validate(df_avec_trous, "TEST")
    assert pd.Timestamp("2025-01-02") in result.index
    assert result.loc[pd.Timestamp("2025-01-02"), "Close"] == 101


def test_volume_manquant_devient_zero(df_avec_trous):
    result = _validate(df_avec_trous, "TEST")
    assert result.loc[pd.Timestamp("2025-01-02"), "Volume"] == 0
    assert result["Volume"].isna().sum() == 0