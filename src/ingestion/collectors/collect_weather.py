from src.ingestion.base_collector import BaseCollector, get_cli_args

class WeatherCollector(BaseCollector):
    def __init__(self, years, modes):
        super().__init__(dataset_name="weather", years=years, modes=modes)

    def extract(self, session):
        return session.weather_data

if __name__ == "__main__":
    years, modes = get_cli_args()
    WeatherCollector(years=years, modes=modes).run()