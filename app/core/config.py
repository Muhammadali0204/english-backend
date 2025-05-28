import secrets

from pathlib import Path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.services.connection_manager import ConnectionManager


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    WORDS_COUNT: int = 3600
    WORDS_IN_ONE_UNIT: int = 20
    UNITS_IN_ONE_BOOK: int = 30
    BOOKS_COUNT: int = 6

    ROUND_DURATION: int = 10
    ROUND_WORDS_COUNT: int = 10

    @computed_field
    @property
    def POSTGRESQL_DATABASE_URI(self) -> str:
        return (
            f"asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    LOCAL_HOST: str = "http://localhost:8080"


settings = Settings()

DATABASE_CONFIG = {
    "connections": {"default": settings.POSTGRESQL_DATABASE_URI},
    "apps": {
        "models": {
            "models": ["app.models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

CONNECTION_MANAGER = ConnectionManager()

GAMES = {}
