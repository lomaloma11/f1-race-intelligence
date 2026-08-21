from src.ingestion.base_collector import BaseCollector, get_cli_args


class ResultsCollector(BaseCollector):
    def __init__(self, years, modes):
        super().__init__(dataset_name="results", years=years, modes=modes)

    def extract(self, session):
        session._load_drivers_results()
        return session.results


if __name__ == "__main__":
    years, modes = get_cli_args()
    ResultsCollector(years=years, modes=modes).run()
