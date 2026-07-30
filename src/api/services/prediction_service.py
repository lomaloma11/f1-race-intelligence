from src.ml.predict import RacePredictor

class PredictionService:
    def __init__(self):
        # Inicializa o modelo de ML assim que o serviço for chamado
        self.predictor = RacePredictor()

    def predict_top10(self, data: dict):
        """
        Extrai os dados do JSON recebido da web e faz a predição.
        """
        # Pega os valores enviados pelo usuário (ou usa um valor padrão se faltar algum)
        grid_position = data.get('grid_position', 20)
        avg_lap_time = data.get('avg_lap_time', 90.0)
        std_lap_time = data.get('std_lap_time', 1.0)
        positions_gained = data.get('positions_gained', 0)
        is_rainy = data.get('is_rainy', 0)

        # Faz a predição usando a classe original
        result = self.predictor.predict_top10(
            grid_position, avg_lap_time, std_lap_time, positions_gained, is_rainy
        )
        return result