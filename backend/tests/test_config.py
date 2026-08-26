"""Test mode configuration for dual testing strategy.

This module provides environment-based test mode detection and configuration
for the dual testing strategy (SQLite quick tests vs PostgreSQL full tests).
"""

from enum import Enum

from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

# Test mode enumeration
class TestMode(Enum):
    """Available test modes."""
    TEST = "test"
    """SQLite quick tests with mocked PostgreSQL types."""
    
    SLOW = "slow"
    """PostgreSQL + PostGIS tests with testcontainers."""


class TestConfig(BaseSettings):
    """Test configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Test mode selection
    test_mode: TestMode = Field(
        default=TestMode.TEST,
        description="Test mode: 'test' for SQLite quick tests, 'slow' for PostgreSQL full tests"
    )

    # SQLite-specific configuration
    sqlite_db_path: str = Field(
        default="./test_quick.db",
        description="SQLite database file path for quick tests"
    )

    # PostgreSQL configuration
    postgres_host: str = Field(
        default="localhost",
        description="PostgreSQL host for full tests"
    )

    postgres_port: int = Field(
        default=5432,
        description="PostgreSQL port for full tests"
    )

    postgres_db: str = Field(
        default="jumapp_test",
        description="PostgreSQL database name for full tests"
    )

    postgres_user: str = Field(
        default="postgres",
        description="PostgreSQL user for full tests"
    )

    postgres_password: str = Field(
        default="postgres",
        description="PostgreSQL password for full tests"
    )

    postgres_schema: str = Field(
        default="test",
        description="PostgreSQL schema for full tests"
    )

    # Test environment configuration
    debug: bool = Field(
        default=True,
        description="Enable debug mode for tests"
    )

    echo_sql: bool = Field(
        default=True,
        description="Echo SQL statements for debugging"
    )

    @property
    def is_sqlite_mode(self) -> bool:
        """Check if SQLite test mode is active."""
        return self.test_mode == TestMode.TEST

    @property
    def is_postgres_mode(self) -> bool:
        """Check if PostgreSQL test mode is active."""
        return self.test_mode == TestMode.SLOW

    @property
    def database_url_sqlite(self) -> str:
        """Get SQLite database URL."""
        return f"sqlite+aiosqlite:///{self.sqlite_db_path}"

    @property
    def database_url_postgres(self) -> str:
        """Get PostgreSQL database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_for_test_mode(self) -> str:
        """Get appropriate database URL for current test mode."""
        if self.is_sqlite_mode:
            return self.database_url_sqlite
        elif self.is_postgres_mode:
            return self.database_url_postgres
        else:
            raise ValueError(f"Invalid test mode: {self.test_mode}")

    @property
    def test_db_type(self) -> str:
        """Get test database type."""
        if self.is_sqlite_mode:
            return "sqlite"
        elif self.is_postgres_mode:
            return "postgres"
        else:
            return "unknown"

    @property
    def test_environment_name(self) -> str:
        """Get test environment name."""
        return self.test_mode.value


def get_test_config() -> TestConfig:
    """Get test configuration from environment."""
    return TestConfig()


def configure_test_environment() -> TestConfig:
    """Configure test environment based on test mode.
    
    This function sets up the test environment for the current test mode,
    including database configuration and type mappings.
    """
    config = get_test_config()

    if config.is_sqlite_mode:
        # Setup SQLite test environment
        print(f"Configured for SQLite tests: {config.test_environment_name}")
        print(f"SQLite database: {config.database_url_sqlite}")
        print("Note: PostgreSQL types (Geography, JSONB) will be mocked")

    elif config.is_postgres_mode:
        # Setup PostgreSQL test environment
        print(f"Configured for PostgreSQL tests: {config.test_environment_name}")
        print(f"PostgreSQL database: {config.database_url_postgres}")
        print("Note: PostGIS extension will be used")

    else:
        raise ValueError(f"Unsupported test mode: {config.test_mode}")

    return config


# Global configuration instance
_test_config: TestConfig | None = None


def set_test_config(config: TestConfig) -> None:
    """Set the global test configuration."""
    global _test_config
    _test_config = config


def get_test_config() -> TestConfig:
    """Get the global test configuration."""
    global _test_config
    if _test_config is None:
        _test_config = TestConfig()
    return _test_config


# Initialize test configuration on module import
_test_config = TestConfig()


def configure_pytest() -> None:
    """Configure pytest based on test mode."""
    config = get_test_config()

    # Configure pytest markers based on test mode
    if config.is_sqlite_mode:
        # Quick test markers
        pytest_plugins = ["pytest_asyncio"]
        marker_expression = "not slow"
    else:
        # Full test markers  
        pytest_plugins = ["pytest_asyncio", "testcontainers"]
        marker_expression = "slow"

    print(f"Pytest configured for {config.test_mode.value} mode")


if __name__ == "__main__":
    # Example usage
    print("Test Configuration Example:")
    config = TestConfig()
    print(f"Test mode: {config.test_mode}")
    print(f"Database URL: {config.database_url_for_test_mode}")
    print(f"Test type: {config.test_db_type}")