from src.ingestion.base_collector import BaseCollector, get_cli_args

class LapsCollector(BaseCollector):
    def __init__(self, years, modes):
        super().__init__(dataset_name="laps", years=years, modes=modes)

    def extract(self, session):
        return session.laps

if __name__ == "__main__":
    years, modes = get_cli_args()
    LapsCollector(years=years, modes=modes).run()