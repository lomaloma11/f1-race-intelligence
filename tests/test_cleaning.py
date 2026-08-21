import pandas as pd
import pytest
from src.data_processing.cleaners.laps_cleaner import LapsCleaner
from src.data_processing.cleaners.results_cleaner import ResultsCleaner
from src.data_processing.cleaners.weather_cleaner import WeatherCleaner


def test_clean_laps():
    raw_data = pd.DataFrame(
        {
            "Driver": ["VER", "VER", "HAM"],
            "LapTime": [
                pd.Timedelta(80.5, unit="s"),
                pd.Timedelta(115.0, unit="s"),
                pd.Timedelta(81.2, unit="s"),
            ],
            "PitOutTime": [pd.NaT, pd.Timedelta(10.0, unit="s"), pd.NaT],
            "PitInTime": [pd.NaT, pd.NaT, pd.NaT],
            "TrackStatus": ["1", "1", "1"],
            "IsAccurate": [True, True, True],
            "LapNumber": [1, 2, 3],
        }
    )

    cleaner = LapsCleaner()
    cleaned_data = cleaner.transform(raw_data)

    assert len(cleaned_data) == 2
    assert "LapTimeSeconds" in cleaned_data.columns
    assert cleaned_data["LapTimeSeconds"].iloc[0] == pytest.approx(80.5)


def test_clean_results():
    raw_data = pd.DataFrame(
        {
            "Abbreviation": ["VER", "HAM", "LEC"],
            "TeamName": ["Red Bull", "Mercedes", "Ferrari"],
            "GridPosition": [1, 2, 3],
            "Position": [1, 2, 3],
            "Points": [25, 18, 15],
            "_ingested_at": [pd.Timestamp.now()] * 3,
        }
    )

    cleaner = ResultsCleaner()
    cleaned_data = cleaner.transform(raw_data)

    assert len(cleaned_data) == 3
    assert "Driver" in cleaned_data.columns
    assert cleaned_data["Driver"].iloc[0] == "VER"
    assert cleaned_data["Position"].iloc[0] == 1


def test_clean_weather():
    raw_data = pd.DataFrame(
        {
            "Humidity": [60, 55, 70],
            "WindSpeed": [5.0, 10.0, 7.5],
            "_ingested_at": [pd.Timestamp.now()] * 3,
        }
    )

    cleaner = WeatherCleaner()
    cleaned_data = cleaner.transform(raw_data)

    assert len(cleaned_data) == 3
    assert "Humidity" in cleaned_data.columns
    assert "WindSpeed" in cleaned_data.columns
    assert cleaned_data["Humidity"].iloc[0] == 60
