import os
import pandas as pd
import fsspec


class BaseProcessor:
    """
    Lê partições Hive de Raw (local ou S3), aplica a sanitização e salva em Silver.
    """

    def __init__(
        self,
        dataset_name: str,
        cleaner_instance,
        raw_dir: str = None,
        silver_dir: str = None,
    ):
        self.dataset_name = dataset_name
        self.cleaner = cleaner_instance

        bucket = os.getenv("S3_BUCKET_NAME")

        if raw_dir:
            self.raw_dir = raw_dir
        elif bucket:
            self.raw_dir = f"s3://{bucket}/raw"
        else:
            self.raw_dir = "data/raw"

        if silver_dir:
            self.silver_dir = silver_dir
        elif bucket:
            self.silver_dir = f"s3://{bucket}/silver"
        else:
            self.silver_dir = "data/silver"

    def _check_exists(self, path: str) -> bool:
        """Verifica a existência do arquivo tanto em disco quanto no S3."""
        fs, fspath = fsspec.core.url_to_fs(path)
        return fs.exists(fspath)

    def process_partition(self, year: int, round_num: int, mode: str = "R"):
        is_raw_s3 = str(self.raw_dir).startswith("s3://")
        is_silver_s3 = str(self.silver_dir).startswith("s3://")

        # Montagem do Caminho de Entrada (Raw)
        if is_raw_s3:
            raw_path = f"{self.raw_dir}/{self.dataset_name}/year={year}/round={round_num:02d}/{mode}.parquet"
        else:
            raw_path = os.path.join(
                self.raw_dir,
                self.dataset_name,
                f"year={year}",
                f"round={round_num:02d}",
                f"{mode}.parquet",
            )

        if not self._check_exists(raw_path):
            return

        # Leitura e Transformação
        df_raw = pd.read_parquet(raw_path)
        df_silver = self.cleaner.transform(df_raw)

        if df_silver is None or (isinstance(df_silver, pd.DataFrame) and df_silver.empty):
            return

        # Montagem do Caminho de Saída (Silver)
        if is_silver_s3:
            output_file = f"{self.silver_dir}/{self.dataset_name}/year={year}/round={round_num:02d}/{mode}.parquet"
        else:
            silver_partition_path = os.path.join(
                self.silver_dir,
                self.dataset_name,
                f"year={year}",
                f"round={round_num:02d}",
            )
            os.makedirs(silver_partition_path, exist_ok=True)
            output_file = os.path.join(silver_partition_path, f"{mode}.parquet")

        # Gravação em Parquet (o Pandas gerencia s3:// via s3fs nativamente)
        df_silver.to_parquet(output_file, index=False, compression="snappy")
        print(
            f" [SILVER] {self.dataset_name.upper()} processado: {year} | Round {round_num:02d} | Modo {mode}"
        )
