import os
import logging
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Keys
    tmdb_api_key: str = ""
    omdb_api_key: str = ""

    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    # Data Paths
    data_dir: Path = Path("cleaned_data")
    movies_file: str = "movies_cleaned.csv"
    ratings_file: str = "ratings_cleaned.csv"
    users_file: str = "user_profiles.csv"

    # Cache Settings
    cache_dir: Path = Path("cache")
    poster_cache_file: str = "poster_cache.json"
    omdb_cache_file: str = "omdb_cache.json"
    battle_data_file: str = "movie_battles.json"
    streaming_data_file: str = "streaming_data.json"
    trivia_data_file: str = "trivia_data.json"

    # API Rate Limits
    tmdb_rate_limit: int = 40  # requests per second
    omdb_rate_limit: int = 1000  # requests per day
    omdb_cache_days: int = 7

    # Recommendation Settings
    default_recommendations: int = 10
    max_recommendations: int = 50
    content_weight: float = 0.6
    collaborative_weight: float = 0.4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def setup_logging(level: str = "INFO"):
    """Configure application logging"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger("moviemate")

def ensure_directories(settings: Settings):
    """Ensure all required directories exist"""
    settings.data_dir.mkdir(exist_ok=True)
    settings.cache_dir.mkdir(exist_ok=True)

# Global settings instance
settings = Settings()

# Set up logging
logger = setup_logging(settings.log_level)

# Ensure directories exist
ensure_directories(settings)
