from pathlib import Path

from pydantic import AnyUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False
    database_url: AnyUrl = AnyUrl("postgresql+psycopg2:///labdic_inventory")
    secret_key: SecretStr = SecretStr("secret123")
    cors_allowed_origins: list[str] = ["*"]
    maintenance_alert_days: int = 30
    overdue_loan_alert_days: int = 0

    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        extra="ignore",
    )


settings = Settings()
