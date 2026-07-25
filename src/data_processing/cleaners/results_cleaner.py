import pandas as pd

class ResultsCleaner:
    """
    Limpa e padroniza os dados de resultado de corrida/sessão para a Camada Silver.
    """
    def transform(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        if df_raw is None or df_raw.empty:
            return pd.DataFrame()

        df = df_raw.copy()

        # Mapeia/Renomeia colunas para manter o padrão das outras tabelas
        rename_map = {
            'Abbreviation': 'Driver',
            'TeamName': 'Team',
            'GridPosition': 'GridPosition',
            'Position': 'Position'
        }
        df = df.rename(columns=rename_map)

        # Garante a conversão numérica de colunas de posição e pontos
        for col in ['Position', 'GridPosition', 'Points']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Colunas essenciais para análise de resultado
        keep_cols = [
            'Driver', 'DriverNumber', 'Team', 'Position', 
            'ClassifiedPosition', 'GridPosition', 'Points', 'Status', '_ingested_at'
        ]
        
        available_cols = [c for c in keep_cols if c in df.columns]
        return df[available_cols].reset_index(drop=True)