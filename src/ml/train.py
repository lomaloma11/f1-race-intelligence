import os
import glob
import json
import joblib
import pandas as pd
import platform
import sklearn

from datetime import datetime, timezone
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


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

    # Definindo a variável Alvo (Target): 1 se terminou no Top 10, 0 caso contrário
    df["is_top10"] = (df["Position"] <= 10).astype(int)

    # Seleção de Features Preditivas
    feature_cols = [
        "GridPosition",
        "avg_lap_time_early",
        "std_lap_time_early",
        "is_rainy_session",
    ]

    # Tratamento de valores nulos (ex: std_lap_time nulo para poucas voltas completadas)
    X = df[feature_cols].copy()
    X = X.fillna(X.median())
    y = df["is_top10"]

    print(f"Dataset pronto: {X.shape[0]} amostras e {X.shape[1]} features.")

    # Divisão Treino / Teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y )

    # Definição do Pipeline (Imputer + Classificador)
    clf = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(n_estimators=100, random_state=42),
            ),
        ]
    )

    # Treinamento do Pipeline completo
    print("Treinando o modelo (Pipeline com SimpleImputer + RandomForest)...")
    clf.fit(X_train, y_train)

    # Validação cruzada (5-fold) no conjunto de treino para checar
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5, scoring="roc_auc")
    print(f"\nROC-AUC (cross-validation 5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Avaliação de Desempenho
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, y_pred, output_dict=True)
    test_auc = roc_auc_score(y_test, y_proba)

    print("\n --- Relatório de Avaliação ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

    # Persistência do Modelo Treinado
    os.makedirs("models", exist_ok=True)
    model_path = "models/top10_model.pkl"
    joblib.dump(clf, model_path)
    print(f"Modelo salvo com sucesso em: {model_path}")

    # Registro versionado das métricas de treino
    metrics_path = "models/metrics_history.json"
    run_record = {
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_path": model_path,
        "feature_cols": feature_cols,
        "n_samples": int(X.shape[0]),
        "n_train": int(X_train.shape[0]),
        "n_test": int(X_test.shape[0]),
        "roc_auc_holdout": round(float(test_auc), 4),
        "roc_auc_cv_mean": round(float(cv_scores.mean()), 4),
        "roc_auc_cv_std": round(float(cv_scores.std()), 4),
        "classification_report": report,
        "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(),
    }

    history = []
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, OSError):
            history = []

    history.append(run_record)
    with open(metrics_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"Métricas registradas em: {metrics_path}")

if __name__ == "__main__":
    train_top10_model()
