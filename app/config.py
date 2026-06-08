try:
    # Prefer pydantic v2 + pydantic-settings
    from pydantic import EmailStr
    from pydantic_settings import BaseSettings
except Exception:
    # Fallback for pydantic v1
    from pydantic import BaseSettings, EmailStr
from typing import Set


class Settings(BaseSettings):
    PROJECT_NAME: str = "نظام الترشح لانتخابات اتحاد طلاب الموهبة والتميز"
    ADMIN_EMAIL: EmailStr = "gtsu.election@gmail.com"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 25
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_ID_MIMES: Set[str] = {"application/pdf", "image/jpeg", "image/png"}
    ALLOWED_PHOTO_MIMES: Set[str] = {"image/jpeg", "image/png"}
    ADMIN_USERNAME: str = "admin"
    # Set ADMIN_PASSWORD in env; default for quick start (change in production)
    ADMIN_PASSWORD: str = "changeme"


settings = Settings()
