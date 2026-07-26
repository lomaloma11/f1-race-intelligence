import os
import pandas as pd
import argparse
from src.data_processing.base_processor import BaseProcessor
from src.data_processing.cleaners.laps_cleaner import LapsCleaner
from src.data_processing.cleaners.results_cleaner import ResultsCleaner
from src.data_processing.cleaners.weather_cleaner import WeatherCleaner
from src.data_processing.feature_engineering import GoldFeatureBuilder

def process_gold_layer(year: int, round_num: int, mode: str = "R"):
    silver_base = "data/silver"
    gold_base = "data/gold"

    # Carrega os três datasets da Silver se existirem
    laps_path = os.path.join(silver_base, "laps", f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")
    results_path = os.path.join(silver_base, "results", f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")
    weather_path = os.path.join(silver_base, "weather", f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")

    df_laps = pd.read_parquet(laps_path) if os.path.exists(laps_path) else None
    df_results = pd.read_parquet(results_path) if os.path.exists(results_path) else None
    df_weather = pd.read_parquet(weather_path) if os.path.exists(weather_path) else None

    if df_results is not None:
        builder = GoldFeatureBuilder()
        df_gold = builder.build_race_features(df_laps, df_results, df_weather)

        # Salva a partição Gold
        gold_partition_path = os.path.join(gold_base, f"year={year}", f"round={round_num:02d}")
        os.makedirs(gold_partition_path, exist_ok=True)
        
        output_file = os.path.join(gold_partition_path, f"{mode}.parquet")
        df_gold.to_parquet(output_file, index=False, compression="snappy")
        print(f"[GOLD] Tabela consolidada gerada: {year} | Round {round_num:02d} | Modo {mode}")


def main():
    parser = argparse.ArgumentParser(description="Orquestrador do Pipeline da Camada SILVER da F1")
    parser.add_argument("--years", "-y", nargs="+", type=int, required=True, help="Anos a processar (ex: -y 2023)")
    parser.add_argument("--modes", "-m", nargs="+", default=["R", "S"], help="Sessões (ex: -m R S)")
    
    args = parser.parse_args()

    # Mapeia cada dataset ao seu respectivo Cleaner
    processors = {
        "laps": BaseProcessor("laps", LapsCleaner()),
        "results": BaseProcessor("results", ResultsCleaner()),
        "weather": BaseProcessor("weather", WeatherCleaner())
    }

    print(f"Iniciando processamento Silver para os anos: {args.years}")

    for year in args.years:
        for round_num in range(1, 30):
            found = False
            for mode in args.modes:
                for dataset_name, processor in processors.items():
                    # Verifica se existe arquivo correspondente na Raw
                    raw_file = os.path.join(
                        "data/raw", dataset_name, f"year={year}", f"round={round_num:02d}", f"{mode}.parquet"
                    )
                    if os.path.exists(raw_file):
                        found = True
                        processor.process_partition(year, round_num, mode)
                        
                    # 2. Processa Gold
                    if found:
                        process_gold_layer(year, round_num, mode)

            # Se não encontrou nenhum dataset para a rodada no modo principal (R), encerra a temporada
            if not found and round_num > 1:
                break

    print("\n Processamento da camada Silver finalizado com sucesso!")

if __name__ == "__main__":
    main()