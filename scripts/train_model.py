import argparse

# Importa as funções de cada modelo criado na pasta src/ml/
from src.ml.train import train_top10_model
from src.ml.tire_degradation import calculate_tire_degradation
from src.ml.driver_clustering import cluster_driving_styles


def main():
    parser = argparse.ArgumentParser(
        description="Orquestrador de Machine Learning da F1"
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        required=True,
        choices=["top10", "tires", "clustering", "all"],
        help="Qual modelo você deseja treinar? (top10, tires, clustering ou all)",
    )

    args = parser.parse_args()

    if args.model in ["top10", "all"]:
        print("\n --- Treinando Modelo: Previsão de Top 10 ---")
        train_top10_model()

    if args.model in ["tires", "all"]:
        print("\n --- Treinando Modelo: Degradação de Pneus ---")
        # Dá pra testar o modelo tanto para pneus macios quanto duros
        calculate_tire_degradation(compound="SOFT")
        calculate_tire_degradation(compound="HARD")

    if args.model in ["clustering", "all"]:
        print("\n --- Treinando Modelo: Estilo de Pilotagem ---")
        cluster_driving_styles(n_clusters=3)

    print("\n Execução do pipeline de Machine Learning finalizada!")


if __name__ == "__main__":
    main()
