"""
App configuration — loads environment variables with pydantic-settings.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=False)


class Settings:
    """Application settings loaded from environment variables."""

    # WhatsApp Business API
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "")
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "stocksense_verify_2026")

    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://localhost:5432/stocksense"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")


settings = Settings()
