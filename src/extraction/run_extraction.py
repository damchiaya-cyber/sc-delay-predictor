# src/extraction/run_extraction.py
import logging
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text
from src.utils.db import get_db_engine
from src.extraction.weather_api import WeatherAPIExtractor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def initialize_database_schema(engine):
    """Executes 01_schema_setup.sql and 02_seed_data.sql files."""
    with engine.begin() as connection:
        with open("sql/01_schema_setup.sql", "r", encoding="utf-8") as f:
            connection.execute(text(f.read()))
        with open("sql/02_seed_data.sql", "r", encoding="utf-8") as f:
            connection.execute(text(f.read()))
    logging.info("Database schema and seed data initialized successfully.")

def run():
    engine = get_db_engine()
    initialize_database_schema(engine)

    # Load hubs from database
    hubs_df = pd.read_sql_query("SELECT hub_id, latitude, longitude FROM hubs;", con=engine)
    
    # Define date extraction window (e.g., last 14 days)
    end_dt = datetime.now().date()
    start_dt = end_dt - timedelta(days=14)
    
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")

    extractor = WeatherAPIExtractor()
    all_observations = []

    for _, hub in hubs_df.iterrows():
        df_weather = extractor.fetch_hub_weather(
            hub_id=hub["hub_id"],
            latitude=hub["latitude"],
            longitude=hub["longitude"],
            start_date=start_str,
            end_date=end_str
        )
        if df_weather is not None and not df_weather.empty:
            all_observations.append(df_weather)

    if all_observations:
        final_df = pd.concat(all_observations, ignore_index=True)
        
        # Save to raw storage layer
        raw_output_path = "data/raw/weather_observations_raw.csv"
        final_df.to_csv(raw_output_path, index=False)
        logging.info(f"Raw weather observations exported to '{raw_output_path}' ({len(final_df)} records).")

        # Persist to relational database
        with engine.begin() as conn:
            final_df.to_sql("weather_observations", con=conn, if_exists="replace", index=False)
        logging.info("Successfully populated 'weather_observations' table in relational database.")

if __name__ == "__main__":
    run()
