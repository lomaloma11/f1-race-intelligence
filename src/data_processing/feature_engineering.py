import pandas as pd 

class GoldFeatureBuilder:

    def build_race_features(
            self, 
            df_laps: pd.DataFrame,
            df_results: pd.DataFrame,
            df_weather: pd.DataFrame
    ) -> pd.DataFrame:
        if df_results is None or df_results.empty:
            return pd.DataFrame()

        # 1. Métricas Agregadas de Voltas por Piloto (Ritmo e Consistência)
        if df_laps is not None and not df_laps.empty:
            laps_summary = df_laps.groupby('Driver').agg(
                avg_lap_time=('LapTimeSeconds', 'mean'),
                fastest_lap=('LapTimeSeconds', 'min'),
                std_lap_time=('LapTimeSeconds', 'std'),  # Variabilidade (consistência)
                total_valid_laps=('LapNumber', 'count')
            ).reset_index()
        else:
            laps_summary = pd.DataFrame()

        # 2. Métricas agregadas ao clima da corrida
        avg_track_temp = df_weather['TrackTemp'].mean() if (df_weather is not None and 'TrackTemp' in df_weather.columns) else None
        if df_weather is not None and not df_weather.empty and 'Rainfall' in df_weather.columns:
            # .astype(bool).any() garante o retorno True se houver pelo menos 1 minuto de chuva
            is_rainy = int(df_weather['Rainfall'].astype(bool).any())
        else:
            is_rainy = 0
            
        # 3. Consolidação no DataFrame de Resultados
        gold_df = df_results.copy()
        
        if not laps_summary.empty:
            gold_df = pd.merge(gold_df, laps_summary, on='Driver', how='left')

        gold_df['avg_track_temp'] = avg_track_temp
        gold_df['is_rainy'] = is_rainy

        # Calculando alteração de posições (Grid vs Posição Final)
        if 'GridPosition' in gold_df.columns and 'Position' in gold_df.columns:
            gold_df['positions_gained'] = gold_df['GridPosition'] - gold_df['Position']

        return gold_df