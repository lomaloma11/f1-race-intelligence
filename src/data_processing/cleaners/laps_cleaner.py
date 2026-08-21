import pandas as pd


class LapsCleaner:
    """
    Limpa e padroniza os dados brutos de voltas (laps) para a Camada Silver.
    """

    def transform(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        if df_raw is None or df_raw.empty:
            return pd.DataFrame()

        df = df_raw.copy()

        # 1. Filtra apenas voltas com tempo registrado
        df = df.dropna(subset=["LapTime", "LapNumber"])

        # 2. Remove voltas de entrada/saída do box (PitIn / PitOut)
        if "PitOutTime" in df.columns:
            df = df[df["PitOutTime"].isna()]
        if "PitInTime" in df.columns:
            df = df[df["PitInTime"].isna()]

        # 3. Converte colunas de Timedelta para segundos
        time_cols = ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]
        for col in time_cols:
            if col in df.columns:
                df[f"{col}Seconds"] = pd.to_timedelta(df[col]).dt.total_seconds()

        # 4. Seleciona colunas essenciais
        keep_cols = [
            "Driver",
            "DriverNumber",
            "Team",
            "LapNumber",
            "LapTimeSeconds",
            "Sector1TimeSeconds",
            "Sector2TimeSeconds",
            "Sector3TimeSeconds",
            "Stint",
            "Compound",
            "TyreLife",
            "FreshTyre",
            "_ingested_at",
        ]

        available_cols = [c for c in keep_cols if c in df.columns]

        return df[available_cols].reset_index(drop=True)
