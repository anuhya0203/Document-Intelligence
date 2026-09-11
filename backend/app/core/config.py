import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./document_intelligence.db"
    )
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # Validation
    MAX_PAGES = int(os.getenv("MAX_PAGES", "3"))
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))

    ALLOWED_FILE_TYPES = ["pdf", "jpg", "jpeg", "png"]
    ALLOWED_MIME_TYPES = [
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
    ]

    # Financial validation
    NUMERIC_TOLERANCE = float(os.getenv("NUMERIC_TOLERANCE", "0.01"))

    # OCR
    OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "en")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()