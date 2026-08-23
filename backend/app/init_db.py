"""Database setup and seed operations.

This module provides initialization and seeding scripts to set up the database
with PostGIS extension, create all tables, and populate initial test data.
It avoids Alembic for better control and simpler deployment.
"""

import asyncio
from datetime import time

from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.config import settings
from app.db import Base, engine, AsyncSessionLocal

# Import all model classes to ensure they are known to the metadata
from app.models.masjid import Masjid
from app.models.person import MasjidPerson
from app.models.photo import MasjidPhoto
from app.models.program import MasjidProgram, ProgramSchedule
from app.models.salat import SalatSchedule
from app.models.audit import AuditEvent
from app.models.outbox import OutboxEvent


async def create_db() -> None:
    """Create the database and all tables if DB_AUTO_CREATE is True."""
    if not settings.db_auto_create:
        print("DB_AUTO_CREATE is false, skipping database creation")
        return

    # Enable PostGIS extension
    print("Enabling PostGIS extension...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        except Exception as e:
            # Extension might already exist
            if "already exists" in str(e):
                print("PostGIS extension already exists")
            else:
                raise

        # Create all tables
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("Database created successfully!")


async def seed_data() -> None:
    """Populate the database with initial seed data."""
    print("Seeding initial data...")

    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if seed masjid already exists
            result = await session.execute(
                select(Masjid).where(Masjid.name == "Test Masjid")
            )
            if result.scalar_one_or_none() is not None:
                print("Seed data already exists, skipping...")
                return

            # Seed a test masjid
            test_masjid = Masjid(
                name="Test Masjid",
                address_line1="123 Test Street",
                city="Test City",
                state="Test State",
                postal_code="12345",
                country="IN",
                latitude=28.6139,
                longitude=77.2090,
                location=WKTElement("POINT(77.2090 28.6139)", srid=4326),
                timezone="Asia/Kolkata",
                map_id="test_map_id",
                accessible_by_public_transport=True,
                accessibility_details="Accessible via bus and metro",
                highway_masjid=True,
                on_road_masjid=False,
                opens_at=time(5, 0),
                closes_at=time(21, 0),
                is_24_hours=False,
                ramadan_adjusted_hours=None,
                has_wudu_stations=True,
                has_urinals=True,
                has_toilets=True,
                has_womens_prayer_area=True,
                has_library=True,
                has_parking=True,
                has_street_parking=True,
                other_items=None,
                meta={"test": True},
            )

            session.add(test_masjid)
            await session.flush()

            # Seed Salat schedules for the test masjid
            default_salat_times = {
                "fajr": (time(5, 0), time(5, 30)),
                "zuhr": (time(12, 30), time(13, 0)),
                "asr": (time(16, 0), time(16, 30)),
                "maghrib": (time(18, 15), time(18, 30)),
                "isha": (time(19, 45), time(20, 0)),
                "jumuah": (time(12, 30), time(13, 0)),
            }
            for salat_name in ["fajr", "zuhr", "asr", "maghrib", "isha", "jumuah"]:
                adhan_t, iqama_t = default_salat_times[salat_name]
                schedule = SalatSchedule(
                    masjid_id=test_masjid.id,
                    salat_name=salat_name,
                    adhan_time=adhan_t,
                    iqama_time=iqama_t,
                    khutbah_time=time(12, 45) if salat_name == "jumuah" else None,
                )
                session.add(schedule)

            # Seed program for the test masjid
            test_program = MasjidProgram(
                masjid_id=test_masjid.id,
                type="maktab",
                name="Morning Maktab",
                description="Islamic education for children",
                max_participants=50,
                is_active=True,
            )
            session.add(test_program)
            await session.flush()

            # Seed Program schedules
            schedule = ProgramSchedule(
                program_id=test_program.id,
                frequency="daily",
                weekday=None,
                day_of_month=None,
                start_time=time(8, 0),
                end_time=time(9, 0),
            )
            session.add(schedule)

            # Seed a person for the test masjid
            test_person = MasjidPerson(
                masjid_id=test_masjid.id,
                full_name="Test Imam",
                role="imam",
                access_level="admin",
                phone_primary="+91-1234567890",
                phone_alternate=None,
                email="test@masjid.com",
                skills="Quran recitation, Arabic",
                bio="Experienced Imam with 10 years of service",
                photo_url="https://example.com/test.jpg",
                is_active=True,
            )
            session.add(test_person)

            # Seed a test photo
            # test_photo = MasjidPhoto(
            #     masjid_id=test_masjid.id,
            #     filename="test_photo.jpg",
            #     file_path="/uploads/test_photo.jpg",
            #     mime_type="image/jpeg",
            #     size=1024000,
            #     width=1920,
            #     height=1080,
            #     caption="Test photo",
            #     order=0,
            # )
            # session.add(test_photo)

    print("Seed data added successfully!")


async def init_db() -> None:
    """Initialize the database with PostGIS extension and tables."""
    await create_db()
    await seed_data()
    print("Database initialization complete!")


async def check_db() -> bool:
    """Check if the database and required tables exist."""
    try:
        async with engine.begin() as conn:
            # Check if PostGIS is available
            result = await conn.execute(text("SELECT PostGIS_Version()"))
            await result.scalar()

            # Check if our main tables exist
            for table in ["masjids", "salat_schedules", "masjid_programs", "masjid_people", "masjid_photos"]:
                result = await conn.execute(
                    text(f"SELECT to_regclass('{table}')")
                )
                if result.scalar() is None:
                    print(f"Table {table} does not exist")
                    return False

            print("Database and tables exist")
            return True
    except Exception as e:
        print(f"Database check failed: {e}")
        return False


async def main() -> None:
    """Main function to run database initialization."""
    if await check_db():
        print("Database already exists, skipping initialization")
    else:
        await init_db()


if __name__ == "__main__":
    asyncio.run(main())
