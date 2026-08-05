import os
import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class S3DataLake:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region
        )

    def upload_dataframe(self, df : pd.DataFrame, s3_path : str) -> None:
        """ Grava um DataFrame Pandas diretamente em Parquet no S3 """
        full_s3_uri = f"s3://{self.bucket_name}/{s3_path}"
        storage_options = {
            "key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "client_kwargs": {"region_name": self.region}
        }

        df.to_parquet(full_s3_uri, index=False, storage_options=storage_options)
        print(f"Ficheiro guardado com sucesso no S3: {full_s3_uri}")

    def read_dataframe(self, s3_path : str) -> pd.DataFrame:
        """ Lê um ficheiro Parquet diretamente do S3 """
        full_s3_uri = f"s3://{self.bucket_name}/{s3_path}"
        storage_options = {
            "key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "client_kwargs": {"region_name": self.region}
        }

        return pd.read_parquet(full_s3_uri, storage_options=storage_options)