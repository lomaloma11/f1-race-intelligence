import joblib

class AnalyticsService:
    def __init__(self):
        # 1. Carrega os modelos de Pneus
        self.tire_soft_model = joblib.load("models/tire_soft_model.pkl")
        self.tire_hard_model = joblib.load("models/tire_hard_model.pkl")

        # 2. Carrega o pacote de Clusterização
        cluster_artifacts = joblib.load("models/driver_clustering_model.pkl")
        self.scaler = cluster_artifacts["scaler"]
        self.kmeans = cluster_artifacts["kmeans"]

    def get_tire_degradation(self, compound: str):
        """
        Retorna o ritmo base e a degradação por volta de um composto.
        """
        compound = compound.upper()
        if compound == "SOFT":
            model = self.tire_soft_model
        elif compound == "HARD":
            model = self.tire_hard_model
        else:
            raise ValueError(f"Composto '{compound}' não suportado.")

        return {
            "compound": compound,
            "base_pace_seconds": round(model.intercept_, 3),
            "degradation_per_lap_seconds": round(model.coef_[0], 3)
        }

    def predict_cluster(self, avg_lap_time: float, std_lap_time: float):
        """
        Recebe o ritmo de um piloto e diz em qual grupo (cluster) ele se encaixa.
        """
        # O Scikit-Learn exige que os dados sejam passados como uma matriz 2D (lista dentro de lista)
        data = [[avg_lap_time, std_lap_time]]
        
        # 1. Usa a "fita métrica" (Scaler) para normalizar os dados novos
        scaled_data = self.scaler.transform(data)
        
        # 2. O "cérebro" (K-Means) diz a qual grupo ele pertence
        cluster = self.kmeans.predict(scaled_data)[0]

        return {
            "avg_lap_time": avg_lap_time,
            "std_lap_time": std_lap_time,
            "assigned_cluster": int(cluster) # Convertido para int nativo do Python para o JSON não quebrar
        }