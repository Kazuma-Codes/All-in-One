from pydantic import model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION: str = "us-east-1"

    GUEST_EMAIL_DOMAIN: str = "guest.local"
    GUEST_FILE_TTL_HOURS: int = 24
    GUEST_PURGE_DAYS: int = 7
    SECRET_KEY: str = "super-secret-key-change-in-prod"
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    @model_validator(mode="after")
    def normalize_database_url(self):
        if self.DATABASE_URL.startswith(("postgres://", "postgresql://")):
            self.DATABASE_URL = self.DATABASE_URL.replace("://", "+psycopg://", 1)
        return self

    class Config:
        env_file = ".env"

settings = Settings()