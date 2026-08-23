"""Database health check and setup validation."""

import asyncio
from datetime import datetime

from sqlalchemy import text

from app.db import engine
from app.config import settings


async def check_database() -> bool:
    """Check database connectivity and required extensions."""
    try:
        async with engine.connect() as conn:
            # Test basic connectivity
            await conn.execute(text("SELECT 1"))

            # Check for PostGIS extension
            result = await conn.execute(text("SELECT PostGIS_Version()"))
            result.scalar()

            # Check for UUID generation function
            try:
                await conn.execute(text("SELECT gen_random_uuid()"))
            except:
                pass  # Not critical for some databases

        return True
    except Exception as e:
        print(f"Database check failed: {e}")
        return False


def validate_config() -> bool:
    """Validate application configuration."""
    errors = []

    # Check database URL
    if not settings.database_url:
        errors.append("DATABASE_URL is not configured")

    # Check file upload directory
    import os
    if not os.path.exists(settings.upload_dir):
        try:
            os.makedirs(settings.upload_dir, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create upload directory: {e}")

    return len(errors) == 0


async def run_health_check() -> dict:
    """Run complete health check."""
    timestamp = datetime.utcnow()

    config_ok = validate_config()
    db_ok = await check_database()

    return {
        "status": "healthy" if (config_ok and db_ok) else "unhealthy",
        "timestamp": timestamp.isoformat(),
        "checks": {
            "config": {
                "status": "ok" if config_ok else "failed",
                "errors": [] if config_ok else ["Invalid configuration"],
            },
            "database": {
                "status": "ok" if db_ok else "failed",
                "errors": [] if db_ok else ["Database check failed"],
            },
        },
        "config": {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "auth_mode": settings.auth_mode,
            "storage_provider": settings.storage_provider,
            "db_auto_create": settings.db_auto_create,
        },
    }


if __name__ == "__main__":
    import sys

    async def main() -> None:
        result = await run_health_check()
        print(f"Status: {result['status']}")
        print(f"Timestamp: {result['timestamp']}")

        for check_name, check_result in result["checks"].items():
            print(f"{check_name}: {check_result['status']}")

        if result["status"] == "unhealthy":
            sys.exit(1)

    asyncio.run(main())
