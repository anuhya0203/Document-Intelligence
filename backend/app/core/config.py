from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ===========================
    # Gemini
    # ===========================
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # ===========================
    # OCR.space
    # ===========================
    OCR_SPACE_API_KEY: str

    # ===========================
    # Database
    # ===========================
    DATABASE_URL: str = "sqlite:///./document_intelligence.db"
    SQLALCHEMY_ECHO: bool = False

    # ===========================
    # Application
    # ===========================
    APP_NAME: str = "Document Intelligence API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"

    # ===========================
    # File Validation
    # ===========================
    ALLOWED_FILE_TYPES: List[str] = [
        "pdf",
        "jpg",
        "jpeg",
        "png",
    ]

    MAX_FILE_SIZE_MB: int = 10

    MAX_PDF_PAGES: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()