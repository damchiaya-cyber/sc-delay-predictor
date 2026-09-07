# src/utils/db.py
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db_engine(db_url: str = None) -> Engine:
    """
    Creates and returns a SQLAlchemy Database Engine.
    Defaults to local SQLite database if no environment variable is supplied.
    """
    if not db_url:
        db_url = os.getenv("DATABASE_URL", "sqlite:///sc_logistics.db")
    
    logging.info(f"Connecting to database engine...")
    engine = create_engine(db_url, echo=False)
    return engine
