# Supply Chain & Logistics Delay Predictor

An enterprise-grade ML pipeline and analytics system engineered for European FMCG & logistics operations. Predicts delivery delays, models weather/traffic disruptions, and surfaces risk metrics via BI dashboards.

## System Architecture
1. **Extraction**: Open-Meteo REST API & Traffic routing APIs.
2. **Data Warehouse**: PostgreSQL/SQLite relational model.
3. **ML Engine**: XGBoost delay risk classification & lead-time regression.
4. **BI Layer**: Power BI dashboards for SLA violation alerts.
