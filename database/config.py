from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Database settings using Pydantic BaseSettings."""

    postgres_user: str = ""
    postgres_password: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = ""
    database_url: str | None = None

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # Echo SQL statements for debugging
    echo_sql: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def get_database_url(self) -> str:
        """Get the complete database URL for SQLAlchemy.

        Returns:
            The postgresql+asyncpg connection URL.
        """
        if self.database_url:
            return self.database_url

        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
