import argparse

# Importa as classes/funções de cada arquivo individual
from src.ingestion.collectors.collect_laps import LapsCollector
from src.ingestion.collectors.collect_results import ResultsCollector
from src.ingestion.collectors.collect_weather import WeatherCollector


def main():
    parser = argparse.ArgumentParser(description="Orquestrador da Camada RAW da F1")
    parser.add_argument(
        "--years",
        "-y",
        nargs="+",
        type=int,
        required=True,
        help="Lista de anos (ex: -y 2023)",
    )
    parser.add_argument(
        "--modes", "-m", nargs="+", default=["R", "S"], help="Sessões (ex: -m R S)"
    )

    args = parser.parse_args()

    print(f" Iniciando coleta para os anos: {args.years}")

    # 1. Coleta de Voltas
    print("\n--- [1/3] Coletando Laps ---")
    LapsCollector(years=args.years, modes=args.modes).run()

    # 2. Coleta de Resultados
    print("\n--- [2/3] Coletando Results ---")
    ResultsCollector(years=args.years, modes=args.modes).run()

    # 3. Coleta do Clima
    print("\n--- [3/3] Coletando Weather ---")
    WeatherCollector(years=args.years, modes=args.modes).run()

    print("\n Todas as coletas foram finalizadas!")


if __name__ == "__main__":
    main()
