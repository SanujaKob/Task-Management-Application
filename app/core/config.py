from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # lowercase field names, map to UPPERCASE env vars via alias
    secret_key: str = Field("dev", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    database_url: str = Field("sqlite:///./taskmanager.db", alias="DATABASE_URL")

    admin_email: str | None = Field(None, alias="ADMIN_EMAIL")
    admin_password: str | None = Field(None, alias="ADMIN_PASSWORD")
    admin_full_name: str | None = Field(None, alias="ADMIN_FULL_NAME")

    # pydantic‑settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",             # ignore stray env keys
        populate_by_name=True,      # allow population via field names or aliases
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
