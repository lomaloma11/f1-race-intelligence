import os
import time
import argparse
import pandas as pd
from src.ingestion.fastf1_client import FastF1Client


class BaseCollector:
    """
    Classe base que gerencia o loop de execucao, o particionamento Hive e a escrita em Parquet.
    """

    def __init__(
        self,
        dataset_name: str,
        years: list[int],
        modes: list[str],
        output_dir: str = "data/raw",
    ):
        self.client = FastF1Client()
        self.dataset_name = dataset_name
        self.years = years
        self.modes = modes
        self.output_dir = output_dir

    def extract(self, session) -> pd.DataFrame:
        raise NotImplementedError("Implemente o metodo extract() na subclasse.")

    def save(self, df: pd.DataFrame, year: int, round_num: int, mode: str):
        # Particionamento automatico Hive: data/raw/dataset/year=YYYY/round=RR/mode.parquet
        partition_path = os.path.join(
            self.output_dir, self.dataset_name, f"year={year}", f"round={round_num:02d}"
        )
        os.makedirs(partition_path, exist_ok=True)

        file_path = os.path.join(partition_path, f"{mode}.parquet")
        df.to_parquet(file_path, index=False, compression="snappy")

    def process_session(self, year: int, round_num: int, mode: str) -> bool:
        session = self.client.get_session(year, round_num, mode)
        if session is None:
            return False

        try:
            df = self.extract(session)
        except Exception as e:
            print(
                f" Erro extraindo [{self.dataset_name}] em {year} R{round_num:02d} ({mode}): {e}"
            )
            return False

        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return False

        df = df.copy()
        df["_ingested_at"] = pd.Timestamp.now()

        self.save(df, year, round_num, mode)
        print(
            f" [{self.dataset_name.upper()}] Salvo: {year} | Round {round_num:02d} | Modo {mode}"
        )
        return True

    def run(self):
        for year in self.years:
            print(f"\n Coletando [{self.dataset_name.upper()}] do ano {year}...")
            for round_num in range(1, 30):
                for mode in self.modes:
                    success = self.process_session(year, round_num, mode)

                    # Se falhar a corrida principal (R), encerra os rounds deste ano
                    if not success and mode == "R":
                        print(
                            f" Fim da temporada {year} atingido no round {round_num - 1}."
                        )
                        break
                else:
                    time.sleep(0.5)
                    continue
                break
            time.sleep(1)


def get_cli_args():
    parser = argparse.ArgumentParser(description="Coletor F1 Raw Layer")
    parser.add_argument("--start", type=int, help="Ano inicial")
    parser.add_argument("--stop", type=int, help="Ano final")
    parser.add_argument(
        "--years",
        "-y",
        nargs="+",
        type=int,
        help="Lista de anos (ex: -y 2021 2022 2023)",
    )
    parser.add_argument(
        "--modes", "-m", nargs="+", default=["R", "S"], help="Sessoes (ex: R S Q)"
    )
    args = parser.parse_args()

    if args.years:
        years = args.years
    elif args.start and args.stop:
        years = list(range(args.start, args.stop + 1))
    else:
        years = [2023]

    return years, args.modes
