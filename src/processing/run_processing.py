import logging
import os
import pandas as pd
from sqlalchemy import text
from src.utils.db import get_db_engine

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def build_processed_features():
    engine = get_db_engine()
    logging.info("Loading raw shipments and weather data from database...")

    # Load raw tables
    shipments_df = pd.read_sql_query("SELECT * FROM shipments;", con=engine)
    weather_df = pd.read_sql_query(
        "SELECT * FROM weather_observations;", con=engine
    )
    routes_df = pd.read_sql_query("SELECT * FROM routes;", con=engine)

    # Convert timestamps to datetime objects
    shipments_df["planned_dispatch"] = pd.to_datetime(
        shipments_df["planned_dispatch"]
    )
    shipments_df["actual_dispatch"] = pd.to_datetime(
        shipments_df["actual_dispatch"]
    )
    shipments_df["planned_delivery"] = pd.to_datetime(
        shipments_df["planned_delivery"]
    )
    shipments_df["actual_delivery"] = pd.to_datetime(
        shipments_df["actual_delivery"]
    )

    # 1. Temporal Feature Engineering
    shipments_df["dispatch_hour"] = shipments_df["planned_dispatch"].dt.hour
    shipments_df["dispatch_dayofweek"] = shipments_df[
        "planned_dispatch"
    ].dt.dayofweek
    shipments_df["is_weekend"] = (
        shipments_df["dispatch_dayofweek"].isin([5, 6]).astype(int)
    )

    # 2. Merge Route Details
    shipments_df = shipments_df.merge(routes_df, on="route_id", how="left")

    # 3. Export Processed Feature Dataset
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/shipments_features.csv"
    shipments_df.to_csv(output_path, index=False)

    logging.info(
        f"Processed feature dataset saved to '{output_path}' ({len(shipments_df)} records)."
    )


if __name__ == "__main__":
    build_processed_features()