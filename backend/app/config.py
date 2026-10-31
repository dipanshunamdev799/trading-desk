from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # DB
    database_url: str = "postgresql+asyncpg://trading:trading@127.0.0.1:5432/trading"
    database_url_sync: str = "postgresql+psycopg2://trading:trading@127.0.0.1:5432/trading"

    # Upstox
    upstox_analytics_token: str = ""
    upstox_requests_per_second: float = 5
    tapetide_token: SecretStr = SecretStr("")
    tapetide_fallback_enabled: bool = True
    tapetide_timeout_seconds: float = 15
    tapetide_requests_per_second: float = 2
    ipo_collector_enabled: bool = True
    ipo_refresh_seconds: int = 60
    nifty_collector_enabled: bool = True
    nifty_refresh_seconds: int = 300
    market_stream_enabled: bool = True
    market_stream_max_instruments: int = 1500
    market_stream_stale_seconds: int = 30

    # Paths
    backtests_dir: Path = ROOT / "backtests"
    data_dir: Path = ROOT / "data"

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
