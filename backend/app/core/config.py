from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings for Policy Alpha.

    This class is the single source of truth for configuration values used by
    the backend. Values are loaded from a local .env file when present.
    """

    app_name: str = "Policy Alpha"
    environment: str = "development"
    database_url: str = "sqlite:///./policy_alpha.db"
    database_echo: bool = False
    demo_seed_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_sqlite(self) -> bool:
        """Return True when the configured database is SQLite."""
        return self.database_url.startswith("sqlite")

    @property
    def sqlite_connect_args(self) -> dict[str, bool]:
        """Return SQLite-specific connection arguments when needed."""
        if self.is_sqlite:
            return {"check_same_thread": False}
        return {}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    The cache is useful because configuration is read-only after startup and
    avoids repeatedly constructing a new settings object during the app lifetime.
    """
    return Settings()
