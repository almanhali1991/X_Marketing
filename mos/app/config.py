"""
Configuration and settings for MOS
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Marketing Operating System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_PATH: str = "./data/mos.db"
    
    # NVIDIA NIM API
    NIM_API_KEY: str = ""
    NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NIM_MODEL: str = "meta/llama-3.3-70b-instruct"
    NIM_STRATEGY_MODEL: str = "deepseek-ai/deepseek-r1"
    NIM_MAX_TOKENS: int = 2048
    NIM_TEMPERATURE: float = 0.7
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ADMIN_IDS: List[int] = []
    
    # Scheduler
    SCHEDULER_ENABLED: bool = True
    DEFAULT_POST_TIME: str = "09:00"  # HH:MM format
    
    # Content Sources (RSS/News URLs)
    TREND_SOURCES: List[str] = [
        "https://news.google.com/rss?hl=ar-SA&gl=SA&ceid=SA:ar",
    ]
    
    # Watchlist URLs (configurable RSS/News feeds)
    WATCHLIST_URLS: List[str] = []
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "./logs/mos.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
