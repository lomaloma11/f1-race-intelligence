import os
import glob
import pandas as pd
from src.utils.s3_client import S3DataLake


def upload_full_datalake(layers: list[str] = None):

    if layers is None:
        layers = ["raw", "silver", "gold"]

    s3 = S3DataLake()
    print(f"Iniciando sincronização do Data Lake para o bucket: s3://{s3.bucket_name}/\n")

    for layer in layers:
        base_dir = os.path.join("data", layer)
        if not os.path.exists(base_dir):
            print(f"Camada '{layer}' não encontrada localmente em {base_dir}. Pulando...")
            continue

        parquet_files = glob.glob(os.path.join(base_dir, "**", "*.parquet"), recursive=True)
        if not parquet_files:
            print(f"Nenhum arquivo .parquet encontrado na camada '{layer}'.")
            continue

        print(f"[{layer.upper()}] Encontrados {len(parquet_files)} arquivo(s) para upload.")

        for file_path in parquet_files:
            relative_path = os.path.relpath(file_path, "data")
            s3_key = relative_path.replace("\\", "/")

            print(f"  -> Uploading: {s3_key}")
            df = pd.read_parquet(file_path)
            s3.upload_dataframe(df, s3_key)

    print("\n Sucesso! Todas as camadas foram sincronizadas com o AWS S3!")


if __name__ == "__main__":
    upload_full_datalake()
