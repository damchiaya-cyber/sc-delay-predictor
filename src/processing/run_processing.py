import logging
import os
import pandas as pd
from src.utils.db import get_db_engine

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def build_processed_features():
    engine = get_db_engine()
    logging.info("Loading raw datasets from SQLite...")

    shipments_df = pd.read_sql_query("SELECT * FROM shipments;", con=engine)
    weather_df = pd.read_sql_query(
        "SELECT * FROM weather_observations;", con=engine
    )
    routes_df = pd.read_sql_query("SELECT * FROM routes;", con=engine)

    # Convert timestamps
    shipments_df["planned_dispatch"] = pd.to_datetime(
        shipments_df["planned_dispatch"]
    )
    shipments_df["dispatch_date"] = (
        shipments_df["planned_dispatch"].dt.date.astype(str)
    )

    # 1. Temporal Features
    shipments_df["dispatch_hour"] = shipments_df["planned_dispatch"].dt.hour
    shipments_df["dispatch_dayofweek"] = shipments_df[
        "planned_dispatch"
    ].dt.dayofweek
    shipments_df["is_weekend"] = (
        shipments_df["dispatch_dayofweek"].isin([5, 6]).astype(int)
    )

    # 2. Merge Route Metadata
    shipments_df = shipments_df.merge(routes_df, on="route_id", how="left")

    # 3. Merge Weather Data (Handle column naming variations)
    if not weather_df.empty:
        time_col = next(
            (c for c in ["observation_time", "timestamp", "time", "date"] if c in weather_df.columns),
            None,
        )
        
        if time_col:
            weather_df["date"] = pd.to_datetime(weather_df[time_col]).dt.date.astype(str)
            
            # Identify location identifier column
            loc_col = next(
                (c for c in ["location_id", "hub_id", "city"] if c in weather_df.columns),
                None,
            )

            group_cols = ["date"]
            if loc_col:
                group_cols.append(loc_col)

            weather_agg = (
                weather_df.groupby(group_cols)
                .agg(
                    avg_precipitation=("precipitation_mm", "mean"),
                    avg_wind_speed=("wind_speed_kmh", "mean"),
                )
                .reset_index()
            )

            if loc_col and "origin_hub" in shipments_df.columns:
                shipments_df = shipments_df.merge(
                    weather_agg,
                    left_on=["origin_hub", "dispatch_date"],
                    right_on=[loc_col, "date"],
                    how="left",
                )
            else:
                shipments_df = shipments_df.merge(
                    weather_agg,
                    left_on="dispatch_date",
                    right_on="date",
                    how="left",
                )

    # Fill unmerged weather values
    if "avg_precipitation" not in shipments_df.columns:
        shipments_df["avg_precipitation"] = 0.0
    else:
        shipments_df["avg_precipitation"] = shipments_df["avg_precipitation"].fillna(0.0)

    if "avg_wind_speed" not in shipments_df.columns:
        shipments_df["avg_wind_speed"] = 0.0
    else:
        shipments_df["avg_wind_speed"] = shipments_df["avg_wind_speed"].fillna(0.0)

    # Clean up intermediate columns
    drop_cols = ["dispatch_date", "location_id", "hub_id", "date"]
    shipments_df = shipments_df.drop(
        columns=[c for c in drop_cols if c in shipments_df.columns]
    )

    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/shipments_features.csv"
    shipments_df.to_csv(output_path, index=False)

    logging.info(
        f"Processed dataset saved to '{output_path}' ({len(shipments_df)} records)."
    )


if __name__ == "__main__":
    build_processed_features()