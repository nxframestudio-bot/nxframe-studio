"""NXFRAME STUDIO — Settings"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = "nxframe-change-this-in-production"
    ADMIN_USERNAME: str = "hcsavin"
    ADMIN_PASSWORD: str = "NXFRAME.savin@adminLogin#200507"
    SESSION_EXPIRE_HOURS: int = 8
    DATABASE_URL: str = "sqlite+aiosqlite:///./nxframe.db"
    UPLOAD_DIR: str = "api/static/uploads"
    MAX_FILE_SIZE_MB: int = 10
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "NXFRAME STUDIO"
    SMTP_FROM_EMAIL: str = "nxframestudio@gmail.com"
    CONTACT_RECEIVER_EMAIL: str = "nxframestudio@gmail.com"
    # Set this to your Vercel frontend URL after deploying
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_list(self) -> List[str]:
        origins = [
            "http://localhost:3000",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            self.FRONTEND_URL,
        ]
        return list(set(o for o in origins if o))

    @property
    def max_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
