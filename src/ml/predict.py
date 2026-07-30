import joblib
import pandas as pd
import os

class RacePredictor:
    """
    Classe responsável por carregar o modelo de Machine Learning e realizar
    as inferências (predições) com novos dados.
    """
    def __init__(self, model_path: str = "models/top10_model.pkl"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado em {model_path}. Treine o modelo primeiro!")
        
        # Carrega o modelo pré-treinado da memória
        self.model = joblib.load(model_path)
        print("Modelo Top 10 carregado com sucesso!")

    def predict_top10(self, grid_position: int, avg_lap_time: float, std_lap_time: float, positions_gained: int, is_rainy: int):
        """
        Recebe as métricas de um piloto e prevê a probabilidade dele terminar no Top 10.
        """
        # 1. Monta o DataFrame com a mesma exata estrutura usada no treino
        input_data = pd.DataFrame([{
            'GridPosition': grid_position,
            'avg_lap_time': avg_lap_time,
            'std_lap_time': std_lap_time,
            'positions_gained': positions_gained,
            'is_rainy_session': is_rainy
        }])

        # 2. Faz a predição (0 = Fora dos pontos, 1 = Top 10)
        prediction = self.model.predict(input_data)[0]
        
        # 3. Calcula a probabilidade matemática (certeza do modelo)
        probability = self.model.predict_proba(input_data)[0][1]

        return {
            "will_score_points": bool(prediction == 1),
            "probability_percentage": round(probability * 100, 2)
        }

# --- TESTE LOCAL ---
if __name__ == "__main__":
    predictor = RacePredictor()
    
    print("\n --- Teste de Inferência 1 (Piloto Rápido e Constante) ---")
    # Ex: Largou em 3º, tempo médio 75s, variação baixa (0.5s), manteve posição, sem chuva
    resultado_bom = predictor.predict_top10(
        grid_position=3, 
        avg_lap_time=75.0, 
        std_lap_time=0.5, 
        positions_gained=0, 
        is_rainy=0
    )
    print(resultado_bom)

    print("\n --- Teste de Inferência 2 (Piloto Lento e Errático) ---")
    # Ex: Largou em 18º, tempo médio 79s, variação alta (2.5s), perdeu 2 posições, com chuva
    resultado_ruim = predictor.predict_top10(
        grid_position=18, 
        avg_lap_time=79.0, 
        std_lap_time=2.5, 
        positions_gained=-2, 
        is_rainy=1
    )
    print(resultado_ruim)