import os
import glob
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score


def load_gold_dataset(gold_dir: str = "data/gold") -> pd.DataFrame:
    """
    Carrega e une todas as partições Parquet existentes na camada Gold.
    """
    search_path = os.path.join(gold_dir, "**", "*.parquet")
    files = glob.glob(search_path, recursive=True)

    if not files:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em {gold_dir}")

    df_list = [pd.read_parquet(file) for file in files]
    df_full = pd.concat(df_list, ignore_index=True)
    return df_full


def train_top10_model():
    print("Carregando dataset consolidado da camada Gold...")
    df = load_gold_dataset()

    # 1. Definindo a variável Alvo (Target): 1 se terminou no Top 10, 0 caso contrário
    df["is_top10"] = (df["Position"] <= 10).astype(int)

    # 2. Seleção de Features Preditivas
    feature_cols = [
        "GridPosition",
        "avg_lap_time",
        "std_lap_time",
        "positions_gained",
        "is_rainy_session",
    ]

    # Tratamento de valores nulos (ex: std_lap_time nulo para poucas voltas completadas)
    X = df[feature_cols].copy()
    X = X.fillna(X.median())
    y = df["is_top10"]

    print(f"Dataset pronto: {X.shape[0]} amostras e {X.shape[1]} features.")

    # 3. Divisão Treino / Teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Treinamento do Modelo
    print("Treinando o modelo (RandomForestClassifier)...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # 5. Avaliação de Desempenho
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    print("\n --- Relatório de Avaliação ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

    # 6. Persistência do Modelo Treinado
    os.makedirs("models", exist_ok=True)
    model_path = "models/top10_model.pkl"
    joblib.dump(clf, model_path)
    print(f"Modelo salvo com sucesso em: {model_path}")


if __name__ == "__main__":
    train_top10_model()
