"""
Backend Configuration Module
Owner: Krishna
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cyclone Risk & Action Platform API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    DATABASE_URL: str = "sqlite:///./cyclone_risk.db"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
