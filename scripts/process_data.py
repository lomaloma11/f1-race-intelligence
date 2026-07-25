import os
import argparse
from src.data_processing.base_processor import BaseProcessor
from src.data_processing.cleaners.laps_cleaner import LapsCleaner
from src.data_processing.cleaners.results_cleaner import ResultsCleaner
from src.data_processing.cleaners.weather_cleaner import WeatherCleaner

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
            found_any = False
            for mode in args.modes:
                for dataset_name, processor in processors.items():
                    # Verifica se existe arquivo correspondente na Raw
                    raw_file = os.path.join(
                        "data/raw", dataset_name, f"year={year}", f"round={round_num:02d}", f"{mode}.parquet"
                    )
                    if os.path.exists(raw_file):
                        found_any = True
                        processor.process_partition(year, round_num, mode)

            # Se não encontrou nenhum dataset para a rodada no modo principal (R), encerra a temporada
            if not found_any and round_num > 1:
                break

    print("\n Processamento da camada Silver finalizado com sucesso!")

if __name__ == "__main__":
    main()