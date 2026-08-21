import pandas as pd


class WeatherCleaner:
    """
    Limpa e padroniza os dados climáticos da pista para a Camada Silver.
    """

    def transform(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        if df_raw is None or df_raw.empty:
            return pd.DataFrame()

        df = df_raw.copy()

        # Converte a coluna de tempo decorrido para segundos
        if "Time" in df.columns and pd.api.types.is_timedelta64_dtype(df["Time"]):
            df["TimeSeconds"] = df["Time"].dt.total_seconds()

        # Garante indicador numérico/booleano limpo para ocorrência de chuva
        if "Rainfall" in df.columns:
            df["Rainfall"] = df["Rainfall"].astype(int)

        keep_cols = [
            "TimeSeconds",
            "AirTemp",
            "Humidity",
            "Pressure",
            "Rainfall",
            "TrackTemp",
            "WindSpeed",
            "_ingested_at",
        ]

        available_cols = [c for c in keep_cols if c in df.columns]
        return df[available_cols].reset_index(drop=True)
