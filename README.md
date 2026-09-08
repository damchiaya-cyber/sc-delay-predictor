Set-Content -Path README.md -Value '# 🚚 FMCG Supply Chain Delay Predictor (German Market)

A modular, production-ready Machine Learning pipeline and interactive analytical workspace designed to predict SLA (Service Level Agreement) shipment delay risks across German FMCG logistics networks.

The system integrates route features, temporal dispatch schedules, and real-time environmental observations (Open-Meteo precipitation and wind metrics) into an XGBoost classification pipeline optimized for high recall on rare SLA violations.

---

## 📌 Project Overview

In FMCG logistics, failing to detect delayed shipments leads to missed customer delivery windows, contractual penalties, and high emergency rerouting costs.

* **Objective:** Predict binary SLA violation risk (`is_sla_violated`) prior to or at time of dispatch.
* **Target Recall:** ~96% recall on delay instances using dynamic class-reweighting (`scale_pos_weight`).
* **Interpretable ML:** Integrated SHAP values to explain individual delay risk drivers for supply chain dispatchers.

---

## 🏗 System Architecture

```text
sc-delay-predictor/
├── data/
│   ├── raw/                  # SQLite source database (sc_logistics.db)
│   └── processed/            # Engineered feature matrix (shipments_features.csv)
├── dashboards/
│   ├── .streamlit/
│   │   └── config.toml       # Custom UI theme tokens
│   └── app.py                # Streamlit dispatch risk workspace
├── models/
│   └── xgboost_delay_model.joblib # Trained XGBoost binary classifier artifact
├── sql/                      # Extraction & schema creation scripts
├── src/
│   ├── api/
│   │   └── app.py            # FastAPI REST engine with Pydantic validation
│   ├── models/
│   │   ├── train_model.py    # Training & evaluation pipeline
│   │   └── predict.py        # Independent inference engine
│   ├── processing/
│   │   └── run_processing.py # Data extraction, joining & feature engineering
│   └── utils/
│       └── db.py             # SQLAlchemy/SQLite connector utilities
├── pyproject.toml            # Package build configuration (editable install)
├── requirements.txt          # Frozen dependency manifest
└── README.md