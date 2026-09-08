import logging
import os
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def train_delay_predictor():
    logging.info("Chargement des données transformées...")
    df = pd.read_csv("data/processed/shipments_features.csv")

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

    # 1. Dynamic scale_pos_weight calculation
    num_neg = (y_train == 0).sum()
    num_pos = (y_train == 1).sum()
    scale_weight = num_neg / num_pos
    logging.info(
        f"Calcul du poids des classes - Négatifs: {num_neg}, Positifs: {num_pos} | scale_pos_weight: {scale_weight:.2f}"
    )

    # 2. XGBoost with class balance handling
    logging.info("Entraînement du modèle XGBoost Classifier (avec scale_pos_weight)...")
    model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=5,
        scale_pos_weight=scale_weight,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Model evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    logging.info(f"Performance - Exactitude (Accuracy): {acc:.4f}")
    logging.info(f"Performance - Rappel Classe 1 (Recall): {recall:.4f}")
    logging.info(f"Performance - Score F1: {f1:.4f}")
    print("\nRapport de classification détaillé :\n")
    print(classification_report(y_test, y_pred))

    # Save trained model artifact
    os.makedirs("models", exist_ok=True)
    model_path = "models/xgboost_delay_model.joblib"
    joblib.dump(model, model_path)
    logging.info(f"Modèle sauvegardé avec succès dans '{model_path}'.")


if __name__ == "__main__":
    train_delay_predictor()