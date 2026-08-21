import pandas as pd
import pytest
from src.data_processing.feature_engineering import GoldFeatureBuilder


@pytest.fixture
def sample_silver_data():
    """Gera dados mockados das 3 tabelas Silver para o teste."""
    df_laps = pd.DataFrame(
        {
            "Driver": ["VER", "VER", "VER", "HAM", "HAM", "HAM"],
            "LapNumber": [1, 2, 3, 1, 2, 3],
            "LapTimeSeconds": [80.0, 81.0, 82.0, 82.0, 82.0, 82.0],
        }
    )

    df_results = pd.DataFrame(
        {
            "Driver": ["VER", "HAM"],
            "GridPosition": [3, 1],
            "Position": [1, 2],
            "Points": [25, 18],
        }
    )

    df_weather = pd.DataFrame(
        {
            "TrackTemp": [32.5, 33.0, 31.8],
            "Rainfall": [False, False, False],
        }
    )

    return df_laps, df_results, df_weather


def test_build_race_features(sample_silver_data):
    df_laps, df_results, df_weather = sample_silver_data
    feature_builder = GoldFeatureBuilder()

    df_gold = feature_builder.build_race_features(df_laps, df_results, df_weather)

    assert len(df_gold) == 2
    assert set(df_gold["Driver"]) == {"VER", "HAM"}

    ver_row = df_gold[df_gold["Driver"] == "VER"].iloc[0]
    assert ver_row["avg_lap_time"] == pytest.approx(81.0)
    assert ver_row["std_lap_time"] == pytest.approx(1.0)

    ham_row = df_gold[df_gold["Driver"] == "HAM"].iloc[0]
    assert ham_row["avg_lap_time"] == pytest.approx(82.0)
    assert ham_row["std_lap_time"] == pytest.approx(0.0)

    assert ver_row["positions_gained"] == 2
    assert ham_row["positions_gained"] == -1

    assert ver_row["is_rainy_session"] == 0
    assert ham_row["is_rainy_session"] == 0
