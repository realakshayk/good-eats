from pydantic import BaseSettings, Field
from functools import lru_cache
import os

class Settings(BaseSettings):
    ENV: str = Field("development", env="ENV")
    OPENAI_API_KEY: str = Field("", env="OPENAI_API_KEY")
    GOOGLE_API_KEY: str = Field("", env="GOOGLE_API_KEY")
    REDIS_URI: str = Field("redis://localhost:6379/0", env="REDIS_URI")
    FALLBACK_MODE: bool = Field(False, env="FALLBACK_MODE")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    RATE_LIMIT: int = Field(100, env="RATE_LIMIT")
    SCORING_WEIGHTS_PATH: str = Field("config/scoring_weights.yaml", env="SCORING_WEIGHTS_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 