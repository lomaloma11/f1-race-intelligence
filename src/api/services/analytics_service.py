import joblib
import os
from src.utils.s3_client import S3DataLake

class AnalyticsService:
    def __init__(self):
        # 1. Carrega os modelos de Pneus
        self.tire_soft_model = joblib.load("models/tire_soft_model.pkl")
        self.tire_hard_model = joblib.load("models/tire_hard_model.pkl")

        # 2. Carrega o pacote de Clusterização
        cluster_artifacts = joblib.load("models/driver_clustering_model.pkl")
        self.scaler = cluster_artifacts["scaler"]
        self.kmeans = cluster_artifacts["kmeans"]

        self.S3 = S3DataLake() if os.getenv("S3_BUCKET_NAME") else None

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
        # 1. Carrega o pacote com os dois artefatos
        artifacts = joblib.load("models/driver_clustering_model.pkl")
        scaler = artifacts["scaler"]
        kmeans = artifacts["kmeans"]
        
        # 2. Escalonar os dados (formato de lista 2D)
        scaled_data = scaler.transform([[avg_lap_time, std_lap_time]])
        
        # 3. Fazer a previsão (Isso devolve um numpy.int64)
        cluster_numpy = kmeans.predict(scaled_data)[0]
        
        # 4. CONVERSÃO OBRIGATÓRIA: Transformar em int nativo do Python
        cluster_id = int(cluster_numpy)
        
        return cluster_id