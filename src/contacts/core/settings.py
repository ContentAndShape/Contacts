import logging

from pydantic import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    debug: bool = False
    api_prefix: str = "/api"
    log_level: int = logging.INFO

    db_name: str = 'postgres'
    db_user: str = 'postgres'
    db_password: str = 'root'
    db_host: str = '127.0.0.1'
    db_port: int = 5432

    secret: str

    @property
    def _db_creds(self) -> str:
        return (
            f"{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:"
            f"{self.db_port}/"
            f"{self.db_name}"
        )

    @property
    def db_conn_str(self) -> str:
        return (
            f"postgresql+psycopg2://{self._db_creds}"
        )

    @property
    def async_db_conn_str(self) -> str:
        return (
            f"postgresql+asyncpg://{self._db_creds}"
        )

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
