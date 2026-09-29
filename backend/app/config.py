"""GeoVerify India Configuration Module."""

from typing import List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "GeoVerify India"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/geoverify",
        description="PostgreSQL/PostGIS Connection String"
    )
    USE_SQLITE_FALLBACK: bool = True

    # Geocoding Provider Settings
    GEOCODER_PROVIDER: str = "mock"  # Options: 'mock', 'nominatim'
    GEOCODER_API_KEY: str = ""
    GEOCODER_BASE_URL: str = "https://nominatim.openstreetmap.org"
    GEOCODER_USER_AGENT: str = "GeoVerify-India/1.0"
    GEOCODER_RATE_LIMIT_DELAY: float = 1.0  # seconds between Nominatim calls

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "*"
    ]

    # Verification Scoring Weights (Must sum to 100)
    WEIGHT_HIERARCHY: int = 25
    WEIGHT_BOUNDARY: int = 25
    WEIGHT_LOCALITY: int = 20
    WEIGHT_PINCODE: int = 15
    WEIGHT_GEOCODING: int = 10
    WEIGHT_NEARBY: int = 5

    # Nearby Search Radius
    DEFAULT_NEARBY_RADIUS_KM: float = 5.0
    MAX_NEARBY_PLACES: int = 20

    # Data Retention & Privacy
    ANONYMIZE_LOGS: bool = True
    DATA_RETENTION_DAYS: int = 30

    @property
    def scoring_weights(self) -> Dict[str, int]:
        return {
            "hierarchy": self.WEIGHT_HIERARCHY,
            "boundary": self.WEIGHT_BOUNDARY,
            "locality": self.WEIGHT_LOCALITY,
            "pincode": self.WEIGHT_PINCODE,
            "geocoding": self.WEIGHT_GEOCODING,
            "nearby": self.WEIGHT_NEARBY,
        }


settings = Settings()
