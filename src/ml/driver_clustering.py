import os
import joblib
import pandas as pd
import glob
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def cluster_driving_styles(n_clusters: int = 3):
    print(f" Agrupando pilotos em {n_clusters} perfis de pilotagem...")

    files = glob.glob("data/gold/**/*.parquet", recursive=True)
    if not files:
        print("Nenhum dado Gold encontrado.")
        return  

    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    # Remove pilotos sem dados de ritmo
    df = df.dropna(subset=['avg_lap_time', 'std_lap_time'])
    
    # 2. Seleciona as features: Velocidade e Consistência
    X = df[['avg_lap_time', 'std_lap_time']]
    
    # 3. Normaliza os dados (K-Means é sensível à escala dos números)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. Aplica o K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['DrivingStyle_Cluster'] = kmeans.fit_predict(X_scaled)
    
    # 5. Exibe um resumo dos grupos
    print("\n Perfis Identificados:")
    summary = df.groupby('DrivingStyle_Cluster').agg(
        Pilotos_No_Grupo=('Driver', 'unique'),
        Ritmo_Medio=('avg_lap_time', 'mean'),
        Consistencia_Media=('std_lap_time', 'mean')
    ).round(2)
    
    for cluster, row in summary.iterrows():
        print(f"\n--- CLUSTER {cluster} ---")
        print(f"Ritmo: {row['Ritmo_Medio']}s | Variação (Erro): {row['Consistencia_Media']}s")
        print(f"Pilotos: {', '.join(row['Pilotos_No_Grupo'][:5])}...")

    os.makedirs("models", exist_ok=True)
    model_path = "models/driver_clustering_model.pkl"
        
        # Cria um dicionário (pacote) com os dois artefatos
    artifacts = {
            "scaler": scaler,
            "kmeans": kmeans
    }
        
    joblib.dump(artifacts, model_path)
    print(f"Scaler e Modelo KMeans salvos com sucesso em: {model_path}")

if __name__ == "__main__":
    cluster_driving_styles()