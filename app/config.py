"""
Application Configuration Module
Reads configuration from environment variables or .env file with robust defaults.
"""

import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Application runtime settings."""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "PlantCare AI")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Model & Vision Engine
    MODEL_CONFIDENCE_THRESHOLD: float = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.70"))
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))

    # Geospatial Settings
    DEFAULT_SEARCH_RADIUS_KM: float = float(os.getenv("DEFAULT_SEARCH_RADIUS_KM", "25.0"))
    MAX_SEARCH_RADIUS_KM: float = float(os.getenv("MAX_SEARCH_RADIUS_KM", "100.0"))
    EARTH_RADIUS_KM: float = 6371.0

    # Reservation Settings
    DEFAULT_RESERVATION_HOURS: int = 4
    MAX_RESERVATION_QUANTITY: int = 20

    # Static Directory for Web UI
    STATIC_DIR: Path = Path(__file__).resolve().parent / "static"


settings = Settings()
