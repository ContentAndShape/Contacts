import logging

from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    api_prefix: str = "/api"
    log_level: int = logging.INFO

    db_name: str = 'postgres'
    db_user: str = 'postgres'
    db_password: str = 'root'
    db_host: str = '127.0.0.1'
    db_port: int = 5432

    @property
    def db_conn_str(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:"
            f"{self.db_port}/"
            f"{self.db_name}"
        )

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
