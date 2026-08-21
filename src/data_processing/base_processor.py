import os
import pandas as pd


class BaseProcessor:
    """
    Lê partições Hive de data/raw/, aplica a transformação e salva em data/silver/.
    """

    def __init__(
        self,
        dataset_name: str,
        cleaner_instance,
        raw_dir: str = "data/raw",
        silver_dir: str = "data/silver",
    ):
        self.dataset_name = dataset_name
        self.cleaner = cleaner_instance
        self.raw_dir = raw_dir
        self.silver_dir = silver_dir

    def process_partition(self, year: int, round_num: int, mode: str = "R"):
        # Caminho de entrada (Raw)
        raw_path = os.path.join(
            self.raw_dir,
            self.dataset_name,
            f"year={year}",
            f"round={round_num:02d}",
            f"{mode}.parquet",
        )

        if not os.path.exists(raw_path):
            return

        # Leitura e Transformação
        df_raw = pd.read_parquet(raw_path)
        df_silver = self.cleaner.transform(df_raw)

        if df_silver.empty:
            return

        # Caminho de saída (Silver - espelhando a estrutura de partições)
        silver_partition_path = os.path.join(
            self.silver_dir, self.dataset_name, f"year={year}", f"round={round_num:02d}"
        )
        os.makedirs(silver_partition_path, exist_ok=True)

        output_file = os.path.join(silver_partition_path, f"{mode}.parquet")
        df_silver.to_parquet(output_file, index=False, compression="snappy")
        print(
            f" [SILVER] {self.dataset_name.upper()} processado: {year} | Round {round_num:02d} | Modo {mode}"
        )
