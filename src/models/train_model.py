import logging
import os
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def train_delay_predictor():
    logging.info("Chargement des données transformées...")
    df = pd.read_csv("data/processed/shipments_features.csv")

    # Sélection des caractéristiques (Features) et de la cible (Target)
    feature_cols = [
        "distance_km",
        "expected_duration_hours",
        "sla_max_hours",
        "dispatch_hour",
        "dispatch_dayofweek",
        "is_weekend",
    ]
    target_col = "is_sla_violated"

    X = df[feature_cols]
    y = df[target_col]

    # Séparation Entraînement / Test (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Entraînement du modèle XGBoost
    logging.info("Entraînement du modèle XGBoost Classifier...")
    model = XGBClassifier(
        n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42
    )
    model.fit(X_train, y_train)

    # Évaluation du modèle
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    logging.info(f"Performance du modèle - Exactitude (Accuracy): {acc:.4f}")
    logging.info(f"Performance du modèle - Score F1: {f1:.4f}")
    print("\nRapport de classification détaillé :\n")
    print(classification_report(y_test, y_pred))

    # Sauvegarde du modèle entraîné
    os.makedirs("models", exist_ok=True)
    model_path = "models/xgboost_delay_model.joblib"
    joblib.dump(model, model_path)
    logging.info(f"Modèle sauvegardé avec succès dans '{model_path}'.")


if __name__ == "__main__":
    train_delay_predictor()