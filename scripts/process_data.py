import os
import pandas as pd
import argparse
import fsspec
from src.data_processing.base_processor import BaseProcessor
from src.data_processing.cleaners.laps_cleaner import LapsCleaner
from src.data_processing.cleaners.results_cleaner import ResultsCleaner
from src.data_processing.cleaners.weather_cleaner import WeatherCleaner
from src.data_processing.feature_engineering import GoldFeatureBuilder

def check_path_exists(path: str) -> bool:
    """Verifica se um caminho existe tanto em disco local quanto em s3://."""
    fs, fspath = fsspec.core.url_to_fs(path)
    return fs.exists(fspath)

def get_base_uri(layer: str) -> str:
    """Define o caminho base da camada (S3 ou disco local)."""
    bucket = os.getenv("S3_BUCKET_NAME")
    if bucket:
        return f"s3://{bucket}/{layer}"
    return os.path.join("data", layer)

def process_gold_layer(year: int, round_num: int, mode: str = "R"):
    silver_base = get_base_uri("silver")
    gold_base = get_base_uri("gold")

    is_s3 = silver_base.startswith("s3://")

    # Monta os caminhos dos 3 datasets da camada Silver
    if is_s3:
        laps_path = f"{silver_base}/laps/year={year}/round={round_num:02d}/{mode}.parquet"
        results_path = f"{silver_base}/results/year={year}/round={round_num:02d}/{mode}.parquet"
        weather_path = f"{silver_base}/weather/year={year}/round={round_num:02d}/{mode}.parquet"
        output_file = f"{gold_base}/year={year}/round={round_num:02d}/{mode}.parquet"
    else:
        laps_path = os.path.join(silver_base, "laps", f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")
        results_path = os.path.join(silver_base, "results", f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")
        weather_path = os.path.join(silver_base, "weather", f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")
        gold_partition_path = os.path.join(gold_base, f"year={year}", f"round={round_num:02d}")
        os.makedirs(gold_partition_path, exist_ok=True)
        output_file = os.path.join(gold_partition_path, f"{mode}.parquet")

    # Leitura dos datasets se existirem
    df_laps = pd.read_parquet(laps_path) if check_path_exists(laps_path) else None
    df_results = pd.read_parquet(results_path) if check_path_exists(results_path) else None
    df_weather = pd.read_parquet(weather_path) if check_path_exists(weather_path) else None

    if df_results is not None and not df_results.empty:
        builder = GoldFeatureBuilder()
        df_gold = builder.build_race_features(df_laps, df_results, df_weather)

        # Salva o arquivo consolidado (local ou S3)
        df_gold.to_parquet(output_file, index=False, compression="snappy")
        print(f"[GOLD] Tabela consolidada gerada: {year} | Round {round_num:02d} | Modo {mode}")


def main():
    parser = argparse.ArgumentParser(
        description="Orquestrador do Pipeline da Camada SILVER da F1"
    )
    parser.add_argument(
        "--years",
        "-y",
        nargs="+",
        type=int,
        required=True,
        help="Anos a processar (ex: -y 2023)",
    )
    parser.add_argument(
        "--modes", "-m", nargs="+", default=["R", "S"], help="Sessões (ex: -m R S)"
    )

    args = parser.parse_args()

    processors = {
        "laps": BaseProcessor("laps", LapsCleaner()),
        "results": BaseProcessor("results", ResultsCleaner()),
        "weather": BaseProcessor("weather", WeatherCleaner()),
    }

    raw_base = get_base_uri("raw")
    is_s3 = raw_base.startswith("s3://")

    print(f"Iniciando processamento para os anos: {args.years}")

    for year in args.years:
        for round_num in range(1, 30):
            found_in_round = False

            for mode in args.modes:
                mode_found = False
                # Processa cada dataset da Silver
                for dataset_name, processor in processors.items():
                    if is_s3:
                        raw_file = f"{raw_base}/{dataset_name}/year={year}/round={round_num:02d}/{mode}.parquet"
                    else:
                        raw_file = os.path.join(raw_base, dataset_name, f"year={year}", f"round={round_num:02d}", f"{mode}.parquet")

                    if check_path_exists(raw_file):
                        mode_found = True
                        found_in_round = True
                        processor.process_partition(year, round_num, mode)

                # Processa a Gold
                if mode_found:
                    process_gold_layer(year, round_num, mode)

            # Se não encontrou nenhum dataset para a rodada, encerra a temporada
            if not found_in_round and round_num > 1:
                break

    print("\n Processamento das camadas finalizado com sucesso!")


if __name__ == "__main__":
    main()
