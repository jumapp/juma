"""Application configuration using pydantic-settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    app_name: str = "Jumapp API"
    app_version: str = "0.1.0"
    debug: bool = False

    # CORS
    cors_origins: list[str] = [
        "http://localhost:8081",  # Expo web dev server
        "http://localhost:19006",  # Expo web (legacy)
        "http://localhost:3000",  # Common dev server
    ]

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jumapp"
    db_echo: bool = False
    db_auto_create: bool = False

    # Auth (dev mode until an identity provider is selected)
    auth_mode: str = "dev"
    super_admin_token: str = "dev-super-admin-token"

    # Photo storage
    upload_dir: str = "uploads"
    upload_url_prefix: str = "/uploads"
    max_upload_size_bytes: int = 5 * 1024 * 1024
    max_photos_per_masjid: int = 5

    # GCS (leave empty until credentials are provisioned; local storage is used then)
    gcs_bucket: str = ""
    gcs_project_id: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("auth_mode")
    @classmethod
    def _validate_auth_mode(cls, value: str) -> str:
        if value != "dev":
            raise ValueError("only auth_mode=dev is currently supported")
        return value

    @property
    def storage_provider(self) -> str:
        return "gcs" if self.gcs_bucket else "local"


settings = Settings()
