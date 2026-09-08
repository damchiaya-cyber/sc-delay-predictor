import logging
import joblib
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

MODEL_PATH = "models/xgboost_delay_model.joblib"


def predict_shipment_delay(shipment_data: dict) -> dict:
    """Predicts delay risk for a single shipment or batch.

    Expected keys:
        - distance_km (float)
        - expected_duration_hours (float)
        - sla_max_hours (float)
        - dispatch_hour (int)
        - dispatch_dayofweek (int)
        - is_weekend (int)
        - avg_precipitation (float)
        - avg_wind_speed (float)
    """
    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([shipment_data])
    feature_cols = [
        "distance_km",
        "expected_duration_hours",
        "sla_max_hours",
        "dispatch_hour",
        "dispatch_dayofweek",
        "is_weekend",
        "avg_precipitation",
        "avg_wind_speed",
    ]

    # Predict delay probability
    delay_prob = float(model.predict_proba(df[feature_cols])[:, 1][0])
    is_delayed = int(delay_prob >= 0.5)

    return {
        "delay_prediction": is_delayed,
        "delay_probability": round(delay_prob, 4),
        "risk_level": "HIGH" if delay_prob > 0.6 else ("MEDIUM" if delay_prob > 0.3 else "LOW"),
    }


if __name__ == "__main__":
    # Test inference on a sample high-risk shipment
    sample_shipment = {
        "distance_km": 680.0,
        "expected_duration_hours": 8.5,
        "sla_max_hours": 9.0,
        "dispatch_hour": 18,
        "dispatch_dayofweek": 4,  # Friday
        "is_weekend": 0,
        "avg_precipitation": 12.5,  # Heavy rain
        "avg_wind_speed": 45.0,  # High wind
    }

    result = predict_shipment_delay(sample_shipment)
    logging.info(f"Inference Result: {result}")