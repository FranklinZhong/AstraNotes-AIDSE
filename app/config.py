"""Centralised application settings.

All environment variables are read here — never call os.getenv() in other modules.

Usage:
    from app.config import settings
    secret = settings.jwt_secret
"""
import os


class Settings:
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./notes.db")
    jwt_expire_hours: int = 24


settings = Settings()
