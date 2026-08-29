# App configuration using pydantic-settings.

from enum import Enum

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from tests.test_config import TestMode, get_test_config
except ImportError:
    from backend.tests.test_config import TestMode, get_test_config


class DatabaseEnvironment(Enum):
    """Database environment enumeration."""

    PRODUCTION = "production"
    """Production database with PostgreSQL/PostGIS."""

    TEST = "test"
    """SQLite test database with mocked PostgreSQL types."""

    POSTGRES = "postgres"
    """PostgreSQL test database with Testcontainers."""


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

    # Database configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jumapp"
    database_url_sqlite: str = "sqlite+aiosqlite:///./test.db"
    database_url_postgres: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jumapp_test"

    db_echo: bool = False
    db_auto_create: bool = False

    # Test environment configuration
    test_mode: TestMode = TestMode.TEST
    is_test_environment: bool = False

    # Auth (dev mode until an identity provider is selected)
    auth_mode: str = "dev"
    super_admin_token: str = "dev-super-admin-token"

    # Photo storage
    upload_dir: str = "uploads"
    upload_url_prefix: str = "/uploads"
    max_upload_size_bytes: int = 5 * 1024 * 1024
    max_photos_per_masjid: int = 5

    # Redis cache (Phase 2)
    redis_url: str = ""

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
    def database_url_for_test_mode(self) -> str:
        """Get appropriate database URL for current test mode."""
        test_config = get_test_config()

        if test_config.is_sqlite_mode:
            return self.database_url_sqlite
        elif test_config.is_postgres_mode:
            return self.database_url_postgres
        else:
            return self.database_url

    @property
    def is_sqlite_mode(self) -> bool:
        """Check if SQLite test mode is active."""
        return self.test_mode == TestMode.TEST

    @property
    def is_postgres_mode(self) -> bool:
        """Check if PostgreSQL test mode is active."""
        return self.test_mode == TestMode.SLOW

    @property
    def is_production_mode(self) -> bool:
        """Check if production mode is active."""
        return not self.is_sqlite_mode and not self.is_postgres_mode

    @property
    def test_db_type(self) -> str:
        """Get test database type."""
        if self.is_sqlite_mode:
            return "sqlite"
        elif self.is_postgres_mode:
            return "postgres"
        else:
            return "production"

    @property
    def test_environment_name(self) -> str:
        """Get test environment name."""
        return self.test_mode.value

    @property
    def storage_provider(self) -> str:
        """Get storage provider."""
        return "gcs" if self.gcs_bucket else "local"


# Load test configuration at module import
try:
    _test_config = get_test_config()
    settings = Settings(test_mode=_test_config.test_mode, is_test_environment=True)
except Exception:
    settings = Settings()


# Initialize test configuration on module import
_test_config = get_test_config()