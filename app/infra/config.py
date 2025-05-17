from pydantic import BaseModel
import os

class Settings(BaseModel):
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8080"))
    api_title: str = os.getenv("API_TITLE", "EagleRock API")
    api_key: str = os.getenv("API_KEY", "dev-secret-key")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    pg_host: str = os.getenv("POSTGRES_HOST", "localhost")
    pg_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    pg_db: str = os.getenv("POSTGRES_DB", "eaglerock")
    pg_user: str = os.getenv("POSTGRES_USER", "eaglerock")
    pg_password: str = os.getenv("POSTGRES_PASSWORD", "eaglerock")

    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))

settings = Settings()
