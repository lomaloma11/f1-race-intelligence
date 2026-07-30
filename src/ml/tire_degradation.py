import os
import joblib
import glob
import pandas as pd
from sklearn.linear_model import LinearRegression

def calculate_tire_degradation(compound: str = "SOFT"):
    """
    Treina um modelo de regressão linear para prever a degradação dos pneus com base em métricas de corrida.
    """
    # 1. Carrega os dados da Camada Silver (voltas limpas)
    files = glob.glob("data/silver/laps/**/*.parquet", recursive=True)
    if not files:
        print("Nenhum dado Silver encontrado.")
        return

    df_list = [pd.read_parquet(file) for file in files]
    df = pd.concat(df_list, ignore_index=True)

    # 2. Filtra os dados de interesse (Remove voltas lentas/anômalas e filtra o composto)
    df_filtered = df[(df['Compound'] == compound) & (df['LapTimeSeconds'] < 100)].copy()

    if df_filtered.empty:
        print(f"Sem dados suficientes para o pneu {compound}.")
        return

    # 3. Prepara X (idade do pneu) e y (tempo da volta)
    X = df_filtered[['TyreLife']].fillna(1)
    y = df_filtered['LapTimeSeconds']
    
    # 4. Treina a Regressão Linear
    model = LinearRegression()
    model.fit(X, y)
    
    # 5. Extrai o coeficiente (a degradação por volta)
    deg_rate = model.coef_[0]
    
    print(f"Ritmo base (pneu novo): {model.intercept_:.2f} segundos")
    print(f"Degradação: O piloto perde cerca de {deg_rate:.3f} segundos por volta!")

    # 6. Salvando o modelo dinamicamente
    os.makedirs("models", exist_ok=True)
    
    # Deixa o nome em minúsculo (ex: tire_soft_model.pkl ou tire_hard_model.pkl)
    model_name = f"tire_{compound.lower()}_model.pkl" 
    model_path = os.path.join("models", model_name)
    
    joblib.dump(model, model_path)
    print(f"Modelo de degradação salvo com sucesso em: {model_path}")

if __name__ == "__main__":
    calculate_tire_degradation(compound="SOFT")
    calculate_tire_degradation(compound="HARD")
    