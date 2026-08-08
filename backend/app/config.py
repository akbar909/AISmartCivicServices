"""
Application configuration.
Reads environment variables via Pydantic BaseSettings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "civic_db"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyARRO9EqpC4KRPHbxLCX-H73_ui_bYTXeo"

    # Cloudinary Image Uploads
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    UPLOAD_DIR: str = "uploads"

    # SMTP Email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM_NAME: str = "AI Smart Civic Services"

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent / ".env")
        env_file_encoding = "utf-8"

    
@lru_cache()
def get_settings() -> Settings:
    return Settings()
