# src/extraction/weather_api.py
import logging
import time
from typing import Dict, Any, List, Optional
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class WeatherAPIExtractor:
    """
    Production REST API connector for Open-Meteo API.
    Fetches hourly weather data for supply chain hubs.
    """
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(self, retries: int = 3, backoff_factor: float = 1.0, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure exponential backoff retry strategy for API stability
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_hub_weather(
        self, 
        hub_id: str, 
        latitude: float, 
        longitude: float, 
        start_date: str, 
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetches hourly weather metrics (temperature, precipitation, snowfall, wind speed) 
        for a specific latitude/longitude coordinate frame.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": [
                "temperature_2m",
                "precipitation",
                "snowfall",
                "wind_speed_10m",
                "weather_code"
            ],
            "timezone": "Europe/Berlin"
        }

        try:
            logging.info(f"Extracting weather for hub '{hub_id}' ({start_date} to {end_date})...")
            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Parse hourly JSON object to DataFrame
            hourly_data = data.get("hourly", {})
            if not hourly_data:
                logging.warning(f"No hourly data returned for hub '{hub_id}'.")
                return None

            df = pd.DataFrame({
                "observation_time": pd.to_datetime(hourly_data["time"]),
                "temperature_c": hourly_data["temperature_2m"],
                "precipitation_mm": hourly_data["precipitation"],
                "snowfall_cm": hourly_data["snowfall"],
                "wind_speed_kmh": hourly_data["wind_speed_10m"],
                "weather_code": hourly_data["weather_code"]
            })

            # Add context keys
            df["hub_id"] = hub_id
            df["observation_id"] = df.apply(
                lambda row: f"{hub_id}_{row['observation_time'].strftime('%Y%m%d%H%M')}", 
                axis=1
            )

            # Reorder columns matching weather_observations database table
            columns_order = [
                "observation_id", "hub_id", "observation_time",
                "temperature_c", "precipitation_mm", "snowfall_cm", 
                "wind_speed_kmh", "weather_code"
            ]
            
            return df[columns_order]

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch weather for hub '{hub_id}': {str(e)}")
            return None
