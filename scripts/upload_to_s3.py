import os
import glob
import pandas as pd
from src.utils.s3_client import S3DataLake


def upload_gold_data():
    print("Iniciando upload da camada Gold (incluindo subpastas) para o AWS S3...")
    s3 = S3DataLake()

    base_gold_dir = os.path.join("data", "gold")

    if not os.path.exists(base_gold_dir):
        print("Pasta 'data/gold' não encontrada!")
        return

    # O '**/*.parquet' com recursive=True encontra todos os .parquet em qualquer subpasta (2022, 2023, etc.)
    parquet_files = glob.glob(
        os.path.join(base_gold_dir, "**", "*.parquet"), recursive=True
    )

    if not parquet_files:
        print(
            "Nenhum arquivo .parquet foi encontrado em 'data/gold' ou suas subpastas."
        )
        return

    print(f"Encontrados {len(parquet_files)} arquivo(s) .parquet para envio.\n")

    for file_path in parquet_files:
        # Mantém a estrutura de subpastas no S3 (ex: gold/2022/arquivo.parquet ou gold/year=2022/arquivo.parquet)
        relative_path = os.path.relpath(file_path, "data")
        s3_path = relative_path.replace("\\", "/")

        print(f"Lendo local: {file_path}")
        print(f"Enviando para: s3://{s3.bucket_name}/{s3_path}")

        df = pd.read_parquet(file_path)
        s3.upload_dataframe(df, s3_path)

    print(
        "\n Sucesso! Todos os dados particionados por ano foram enviados para o AWS S3!"
    )


if __name__ == "__main__":
    upload_gold_data()
