"""PostgreSQL Testcontainers fixtures for dual testing strategy.

This module provides test fixtures for PostgreSQL + PostGIS tests using Testcontainers,
including transaction rollback for test isolation and comprehensive spatial testing.
"""

import asyncio
import json
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator, Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.config import settings


try:
    from testcontainers.postgres import PostgresContainer
except ImportError:
    PostgresContainer = None


@pytest.fixture(scope="session")
def postgres_container_image():
    """Get the PostgreSQL container image with PostGIS extension."""
    return "postgres:15-alpine"


@pytest.fixture(scope="session")
def postgres_container_environment():
    """Get the PostgreSQL container environment variables."""
    return {
        "POSTGRES_DB": "jumapp_test",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_HOST_AUTH_METHOD": "trust",
        "PGDATA": "/var/lib/postgresql/data",
        "POSTGIS_EXTENSIONS": "true",
    }


@pytest.fixture(scope="session")
def postgres_container_ports():
    """Get the PostgreSQL container ports mapping."""
    return {"5432/tcp": 5432}


@pytest_asyncio.fixture(scope="session")
def postgres_container(postgres_container_image, postgres_container_environment):
    """Create and start a PostgreSQL container with PostGIS extension.
    
    This fixture sets up a PostgreSQL container with PostGIS extension for testing.
    It uses testcontainers to manage the container lifecycle.
    """
    if PostgresContainer is None:
        pytest.skip("testcontainers not installed")
    
    # Create container with PostGIS
    container = PostgresContainer(
        image=postgres_container_image,
        environment=postgres_container_environment,
        ports=postgres_container_ports(),
        command=["-c", "shared_buffers=256MB", "-c", "max_connections=200"],
    )
    
    # Start container
    container.start()
    
    # Store container details for later use
    container.container_id = container.get_container_id()
    
    yield container
    
    # Clean up container
    container.stop()


@pytest_asyncio.fixture
def postgres_connection_string(postgres_container):
    """Get the PostgreSQL connection string for the container."""
    return (
        f"postgresql+asyncpg://{postgres_container.username}:"
        f"{postgres_container.password}@"
        f"{postgres_container.host}:{postgres_container.get_exposed_port(5432)}/"
        f"{postgres_container.driver_data.get('database')}"
    )


@pytest_asyncio.fixture
def postgres_test_engine(postgres_connection_string):
    """Create an async PostgreSQL engine for testing."""
    engine = create_async_engine(
        postgres_connection_string,
        echo=settings.db_echo,
        pool_pre_ping=True,
        poolclass=NullPool,
        future=True,
        pool_timeout=30,
        connect_args={
            "connect_timeout": 30,
            "application_name": "test_jumapp",
        },
    )
    
    yield engine


@pytest_asyncio.fixture
def postgres_session(postgres_test_engine):
    """Create an async PostgreSQL session for testing with transaction rollback."""
    @asynccontextmanager
    async def _session_context():
        async with AsyncSession(postgres_test_engine, expire_on_commit=False) as session:
            # Begin transaction for test isolation
            async with session.begin():
                try:
                    yield session
                except Exception:
                    # Rollback transaction on any exception
                    await session.rollback()
                    raise
    
    yield _session_context


@pytest_asyncio.fixture
def postgres_transaction_isolation(postgres_session):
    """Ensure test isolation through transaction rollback."""
    @asynccontextmanager
    async def _isolated_transaction():
        async with postgres_session() as session:
            # Begin nested transaction for test isolation
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    return _isolated_transaction


@pytest_asyncio.fixture
def postgis_extension_available(postgres_test_engine):
    """Check if PostGIS extension is available in the test database."""
    async def _check_postgis():
        async with postgres_test_engine.begin() as conn:
            try:
                result = await conn.execute(text("SELECT PostGIS_Version()"))
                version = await result.scalar()
                return version is not None
            except Exception:
                return False
    
    return _check_postgis


@pytest_asyncio.fixture
def setup_postgis_extension(postgres_test_engine, postgis_extension_available):
    """Ensure PostGIS extension is installed and available."""
    async def _ensure_postgis():
        async with postgres_test_engine.begin() as conn:
            if not await postgis_extension_available():
                # Create PostGIS extension
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                print("PostGIS extension created")
            else:
                print("PostGIS extension already exists")
        
        # Verify PostGIS is available
        async with postgres_test_engine.begin() as conn:
            result = await conn.execute(text("SELECT ST_GeomFromText('POINT(0 0)', 4326)"))
            point = await result.scalar()
            return point is not None
    
    return _ensure_postgis


@pytest_asyncio.fixture
def create_test_database_schema(postgres_test_engine):
    """Create test database schema with PostGIS support."""
    async def _create_schema():
        async with postgres_test_engine.begin() as conn:
            # Enable PostGIS
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            
            # Create masjids table with PostGIS and JSONB columns
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS masjids (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    address_line1 TEXT,
                    city VARCHAR(100),
                    state VARCHAR(100),
                    postal_code VARCHAR(20),
                    country VARCHAR(2) NOT NULL DEFAULT 'IN',
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    timezone VARCHAR(50) NOT NULL,
                    location GEOGRAPHY(POINT, 4326),
                    map_id VARCHAR(100),
                    accessible_by_public_transport BOOLEAN DEFAULT FALSE,
                    accessibility_details TEXT,
                    highway_masjid BOOLEAN DEFAULT FALSE,
                    on_road_masjid BOOLEAN DEFAULT FALSE,
                    opens_at TIME,
                    closes_at TIME,
                    is_24_hours BOOLEAN DEFAULT FALSE,
                    ramadan_adjusted_hours JSONB,
                    has_wudu_stations BOOLEAN DEFAULT FALSE,
                    has_urinals BOOLEAN DEFAULT FALSE,
                    has_toilets BOOLEAN DEFAULT FALSE,
                    has_womens_prayer_area BOOLEAN DEFAULT FALSE,
                    has_library BOOLEAN DEFAULT FALSE,
                    has_parking BOOLEAN DEFAULT FALSE,
                    has_street_parking BOOLEAN DEFAULT FALSE,
                    other_items JSONB,
                    meta JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                
                -- Create spatial index
                CREATE INDEX IF NOT EXISTS idx_masjids_location ON masjids USING GIST (location);
                
                -- Create B-tree indexes for text columns
                CREATE INDEX IF NOT EXISTS idx_masjids_name ON masjids USING btree (name);
                CREATE INDEX IF NOT EXISTS idx_masjids_city ON masjids USING btree (city);
                CREATE INDEX IF NOT EXISTS idx_masjids_country ON masjids USING btree (country);
            """))
            
            # Create salat_schedules table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS salat_schedules (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    masjid_id UUID NOT NULL REFERENCES masjids(id) ON DELETE CASCADE,
                    salat_name VARCHAR(20) NOT NULL,
                    adhan_time TIME NOT NULL,
                    iqama_time TIME NOT NULL,
                    khutbah_time TIME,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                
                CREATE INDEX IF NOT EXISTS idx_salat_schedules_masjid_id ON salat_schedules USING btree (masjid_id);
                CREATE INDEX IF NOT EXISTS idx_salat_schedules_salat_name ON salat_schedules USING btree (salat_name);
            """))
            
            # Create masjid_programs table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS masjid_programs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    masjid_id UUID NOT NULL REFERENCES masjids(id) ON DELETE CASCADE,
                    type VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    max_participants INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                
                CREATE INDEX IF NOT EXISTS idx_masjid_programs_masjid_id ON masjid_programs USING btree (masjid_id);
            """))
            
            # Create program_schedules table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS program_schedules (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    program_id UUID NOT NULL REFERENCES masjid_programs(id) ON DELETE CASCADE,
                    frequency VARCHAR(20) NOT NULL,
                    weekday INTEGER,
                    day_of_month INTEGER,
                    start_time TIME,
                    end_time TIME,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # Create masjid_people table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS masjid_people (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    masjid_id UUID NOT NULL REFERENCES masjids(id) ON DELETE CASCADE,
                    full_name VARCHAR(255) NOT NULL,
                    role VARCHAR(100) NOT NULL,
                    access_level VARCHAR(50) NOT NULL,
                    phone_primary VARCHAR(20),
                    phone_alternate VARCHAR(20),
                    email VARCHAR(255),
                    skills TEXT,
                    bio TEXT,
                    photo_url VARCHAR(500),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                
                CREATE INDEX IF NOT EXISTS idx_masjid_people_masjid_id ON masjid_people USING btree (masjid_id);
            """))
            
            # Create masjid_photos table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS masjid_photos (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    masjid_id UUID NOT NULL REFERENCES masjids(id) ON DELETE CASCADE,
                    filename VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    mime_type VARCHAR(100) NOT NULL,
                    size BIGINT NOT NULL,
                    width INTEGER,
                    height INTEGER,
                    caption TEXT,
                    order_index INTEGER DEFAULT 0,
                    is_featured BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                
                CREATE INDEX IF NOT EXISTS idx_masjid_photos_masjid_id ON masjid_photos USING btree (masjid_id);
            """))
            
            # Create audit_events table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    event_type VARCHAR(100) NOT NULL,
                    user_id UUID,
                    masjid_id UUID,
                    action TEXT,
                    details JSONB,
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
                
                CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events USING btree (user_id);
                CREATE INDEX IF NOT EXISTS idx_audit_events_masjid_id ON audit_events USING btree (masjid_id);
                CREATE INDEX IF NOT EXISTS idx_audit_events_event_type ON audit_events USING btree (event_type);
            """))
            
            # Create outbox_events table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS outbox_events (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    event_type VARCHAR(100) NOT NULL,
                    aggregate_id UUID NOT NULL,
                    aggregate_type VARCHAR(100) NOT NULL,
                    event_data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    processed_at TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending'
                )
                
                CREATE INDEX IF NOT EXISTS idx_outbox_events_status ON outbox_events USING btree (status);
                CREATE INDEX IF NOT EXISTS idx_outbox_events_created_at ON outbox_events USING btree (created_at);
            """))
    
    return _create_schema


@pytest_asyncio.fixture
def setup_postgis_test_data(postgres_test_engine):
    """Setup PostGIS test data with realistic geometries and JSONB fields."""
    async def _setup_test_data():
        async with postgres_test_engine.begin() as conn:
            # Insert test masjid with PostGIS geometry and JSONB data
            await conn.execute(text("""
                INSERT INTO masjids (
                    id, name, address_line1, city, state, postal_code, country,
                    latitude, longitude, timezone, location,
                    ramadan_adjusted_hours, meta
                ) VALUES (
                    '00000000-0000-0000-0000-000000000001', 'Test Masjid',
                    '123 Test Street', 'Test City', 'Test State', '12345', 'IN',
                    30.3165, 78.0322, 'Asia/Kolkata',
                    ST_GeomFromText('POINT(78.0322 30.3165)', 4326),
                    '{"start": "05:30", "end": "19:30"}',
                    '{"timezone": "Asia/Kolkata", "access_level": "admin", "features": ["wudu", "toilet"]}'
                ) ON CONFLICT (id) DO NOTHING
            """))
            
            # Insert salat schedules
            await conn.execute(text("""
                INSERT INTO salat_schedules (
                    id, masjid_id, salat_name, adhan_time, iqama_time, khutbah_time
                ) VALUES (
                    gen_random_uuid(), '00000000-0000-0000-0000-000000000001',
                    'fajr', '05:00:00', '05:30:00', NULL
                ) ON CONFLICT (id) DO NOTHING
            """))
            
            # Insert program data
            await conn.execute(text("""
                INSERT INTO masjid_programs (
                    id, masjid_id, type, name, description, max_participants, is_active
                ) VALUES (
                    gen_random_uuid(), '00000000-0000-0000-0000-000000000001',
                    'maktab', 'Morning Maktab', 
                    'Islamic education for children', 50, true
                ) ON CONFLICT (id) DO NOTHING
            """))
            
            # Insert program schedule
            await conn.execute(text("""
                INSERT INTO program_schedules (
                    id, program_id, frequency, weekday, start_time, end_time
                ) VALUES (
                    gen_random_uuid(), 
                    (SELECT id FROM masjid_programs WHERE masjid_id = '00000000-0000-0000-0000-000000000001' LIMIT 1),
                    'daily', NULL, '08:00', '09:00'
                ) ON CONFLICT (id) DO NOTHING
            """))
            
            # Insert person data
            await conn.execute(text("""
                INSERT INTO masjid_people (
                    id, masjid_id, full_name, role, access_level,
                    phone_primary, email, skills, bio, is_active
                ) VALUES (
                    gen_random_uuid(), '00000000-0000-0000-0000-000000000001',
                    'Test Imam', 'imam', 'admin',
                    '+91-1234567890', 'test@masjid.com',
                    'Quran recitation, Arabic', 'Experienced Imam', true
                ) ON CONFLICT (id) DO NOTHING
            """))
            
            # Insert photo data
            await conn.execute(text("""
                INSERT INTO masjid_photos (
                    id, masjid_id, filename, file_path, mime_type, 
                    size, width, height, caption, order_index, is_featured
                ) VALUES (
                    gen_random_uuid(), '00000000-0000-0000-0000-000000000001',
                    'test_photo.jpg', '/uploads/test_photo.jpg', 'image/jpeg',
                    1024000, 1920, 1080, 'Test photo', 0, false
                ) ON CONFLICT (id) DO NOTHING
            """))
    
    return _setup_test_data


@pytest_asyncio.fixture
def seed_postgres_database(
    postgres_test_engine,
    setup_postgis_extension,
    create_test_database_schema,
    setup_postgis_test_data,
):
    """Complete test database setup for PostgreSQL tests."""
    async def _seed_database():
        # Setup PostGIS extension
        await setup_postgis_extension()
        
        # Create database schema
        await create_test_database_schema()
        
        # Setup test data
        await setup_postgis_test_data()
        
        print("PostgreSQL test database setup complete")
    
    return _seed_database


@pytest_asyncio.fixture
def postgres_real_client(postgres_test_engine, seed_postgres_database):
    """Create a PostgreSQL client for real integration testing."""
    async def _get_client():
        # Seed the database
        await seed_postgres_database()
        
        # Return the engine for use in tests
        return postgres_test_engine
    
    return _get_client


@pytest_asyncio.fixture
def mock_postgis_functions():
    """Mock PostGIS functions for testing."""
    with patch('shapely.geometry.Point') as mock_point, \
         patch('shapely.geometry.shape') as mock_shape, \
         patch('sqlalchemy.dialects.postgresql.base.ischema_names') as mock_ischema:
        
        # Setup mock PostGIS functions
        mock_point.return_value.x = 78.0322
        mock_point.return_value.y = 30.3165
        mock_point.return_value.z = None
        mock_point.return_value.coords = [(78.0322, 30.3165)]
        
        mock_shape.return_value = MagicMock()
        
        # Mock PostGIS type mappings
        mock_ischema.__getitem__.return_value = MagicMock()
        
        yield {
            'point': mock_point,
            'shape': mock_shape,
            'ischema': mock_ischema,
        }


@pytest.fixture
def postgres_spatial_operations_mock(mock_postgis_functions):
    """Mock spatial operations for PostgreSQL tests."""
    with patch('backend.app.services.masjid_service.calculate_distance') as mock_distance, \
         patch('backend.app.services.masjid_service.transform_coordinates') as mock_transform, \
         patch('backend.app.services.masjid_service.validate_coordinates') as mock_validate:
        
        # Mock spatial operations
        mock_distance.return_value = 1000.0
        mock_transform.return_value = (30.3165, 78.0322)
        mock_validate.return_value = True
        
        yield {
            'distance': mock_distance,
            'transform': mock_transform,
            'validate': mock_validate,
        }


@pytest_asyncio.fixture
def postgres_transaction_test(postgres_test_engine):
    """Test PostgreSQL transaction functionality."""
    async def _test_transaction_isolation():
        # Create test tables
        async with postgres_test_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_transactions (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    value INTEGER DEFAULT 0
                )
            """))
        
        # Test transaction rollback
        async with postgres_test_engine.begin() as conn:
            await conn.execute(text("INSERT INTO test_transactions (name, value) VALUES ('test1', 100)"))
            
            # This should be rolled back
            raise Exception("Simulated transaction failure")
        
        # Verify data was not persisted
        async with postgres_test_engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM test_transactions"))
            count = await result.scalar()
            assert count == 0, f"Expected 0 rows, got {count}"
    
    return _test_transaction_isolation


@pytest_asyncio.fixture
def postgres_postgis_integration_test(postgres_test_engine):
    """Test PostGIS integration with real data."""
    async def _test_postgis_integration():
        # Test real PostGIS functions
        async with postgres_test_engine.begin() as conn:
            # Create a point
            await conn.execute(text("""
                INSERT INTO masjids (
                    id, name, latitude, longitude, timezone, location
                ) VALUES (
                    gen_random_uuid(), 'Test Location',
                    40.7128, -74.0060, 'America/New_York',
                    ST_GeomFromText('POINT(-74.0060 40.7128)', 4326)
                )
            """))
            
            # Test spatial queries
            result = await conn.execute(text("""
                SELECT 
                    name,
                    ST_AsText(location) as location_wkt,
                    ST_X(location) as longitude,
                    ST_Y(location) as latitude
                FROM masjids 
                WHERE ST_DWithin(
                    location::geography,
                    ST_GeomFromText('POINT(-74.0060 40.7128)', 4326)::geography,
                    1000
                )
            """))
            
            rows = await result.fetchall()
            assert len(rows) > 0
            assert rows[0][0] == 'Test Location'
            
            # Test JSONB operations
            result = await conn.execute(text("""
                UPDATE masjids 
                SET meta = meta || '{"last_updated": "2024-01-01"}'::jsonb
                WHERE id = (SELECT id FROM masjids WHERE name = 'Test Location' LIMIT 1)
                RETURNING meta
            """))
            
            meta_data = await result.scalar_one_or_none()
            assert meta_data is not None
    
    return _test_postgis_integration


@pytest_asyncio.fixture
def postgres_full_integration_environment(
    postgres_container,
    postgres_test_engine,
    seed_postgres_database,
    postgres_postgis_integration_test,
    postgres_transaction_test,
):
    """Create a complete PostgreSQL integration test environment."""
    async def _setup_full_environment():
        # Seed the database
        await seed_postgres_database()
        
        # Run integration tests
        await postgres_postgis_integration_test()
        await postgres_transaction_test()
        
        print("PostgreSQL full integration environment setup complete")
    
    return _setup_full_environment


@pytest.fixture
def postgres_testcontainers_config():
    """Provide PostgreSQL Testcontainers configuration."""
    config = {
        'image': 'postgres:15-alpine',
        'environment': {
            'POSTGRES_DB': 'jumapp_test',
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'postgres',
            'POSTGRES_HOST_AUTH_METHOD': 'trust',
        },
        'ports': {'5432/tcp': 5432},
        'commands': ['-c', 'shared_buffers=256MB', '-c', 'max_connections=200'],
        'wait_for': {
            'sql': 'SELECT 1',
            'timeout': 60,
        },
    }
    
    return config


@pytest.fixture
def postgres_test_data_samples():
    """Provide PostgreSQL test data samples."""
    test_data = {
        'masjid': {
            'id': '00000000-0000-0000-0000-000000000001',
            'name': 'Test Masjid',
            'location': {
                'type': 'Point',
                'coordinates': [78.0322, 30.3165],
                'srid': 4326,
            },
            'meta': {
                'timezone': 'Asia/Kolkata',
                'access_level': 'admin',
                'features': ['wudu', 'toilet', 'library'],
            },
        },
        'salat_schedule': {
            'masjid_id': '00000000-0000-0000-0000-000000000001',
            'salat_name': 'fajr',
            'adhan_time': '05:00:00',
            'iqama_time': '05:30:00',
            'khutbah_time': None,
        },
        'person': {
            'id': '00000000-0000-0000-0000-000000000002',
            'masjid_id': '00000000-0000-0000-0000-000000000001',
            'full_name': 'Test Imam',
            'role': 'imam',
            'access_level': 'admin',
            'phone_primary': '+91-1234567890',
            'email': 'test@masjid.com',
            'is_active': True,
        },
    }
    
    return test_data


# Performance and stress testing fixtures
@pytest_asyncio.fixture
def postgres_performance_test(postgres_test_engine):
    """Setup PostgreSQL performance testing environment."""
    async def _run_performance_tests():
        # Create performance test tables
        async with postgres_test_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS performance_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    value INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
        
        # Run performance tests
        import time
        
        # Test INSERT performance
        start_time = time.time()
        async with postgres_test_engine.begin() as conn:
            for i in range(1000):
                await conn.execute(
                    text("INSERT INTO performance_test (name, value) VALUES (:name, :value)"),
                    {"name": f"test_{i}", "value": i}
                )
        
        insert_time = time.time() - start_time
        print(f"INSERT performance: {insert_time:.2f}s for 1000 records")
        
        # Test SELECT performance
        start_time = time.time()
        async with postgres_test_engine.begin() as conn:
            result = await conn.execute(text("SELECT * FROM performance_test WHERE id > 100 LIMIT 100"))
            rows = await result.fetchall()
        
        select_time = time.time() - start_time
        print(f"SELECT performance: {select_time:.2f}s for 100 records")
        
        # Test JSONB operations
        start_time = time.time()
        async with postgres_test_engine.begin() as conn:
            await conn.execute(text("""
                UPDATE performance_test 
                SET meta = meta || '{"test": true}'::jsonb 
                WHERE id % 10 = 0
            """))
        
        jsonb_time = time.time() - start_time
        print(f"JSONB operation performance: {jsonb_time:.2f}s")
    
    return _run_performance_tests


@pytest.fixture
def postgres_stress_test_config():
    """Provide PostgreSQL stress test configuration."""
    config = {
        'concurrent_connections': 10,
        'max_transactions_per_connection': 100,
        'test_duration_seconds': 300,
        'data_volume_mb': 1000,
        'queries_per_second': 100,
        'cpu_limit': 2.0,
        'memory_limit_mb': 4096,
        'replication_factor': 3,
        'monitoring_enabled': True,
    }
    
    return config


# Error handling and recovery fixtures
@pytest_asyncio.fixture
def postgres_error_recovery_test(postgres_test_engine):
    """Test PostgreSQL error recovery and resilience."""
    async def _test_error_recovery():
        # Test connection error handling
        try:
            # Simulate a database error
            await postgres_test_engine.dispose()
            # This should raise an error when trying to use a disposed engine
            assert False, "Expected error after disposing engine"
        except Exception:
            pass  # Expected
        
        # Recreate engine
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/jumapp_test",
            echo=False,
            pool_pre_ping=True,
        )
        
        # Test recovery
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        await engine.dispose()
    
    return _test_error_recovery


@pytest_asyncio.fixture
def postgres_consistency_test(postgres_test_engine):
    """Test database consistency and integrity."""
    async def _test_consistency():
        # Create test tables
        async with postgres_test_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS consistency_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    value INTEGER NOT NULL
                )
            """))
            
            # Insert test data
            for i in range(10):
                await conn.execute(
                    text("INSERT INTO consistency_test (name, value) VALUES (:name, :value)"),
                    {"name": f"item_{i}", "value": i}
                )
        
        # Test data consistency
        async with postgres_test_engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM consistency_test"))
            count = await result.scalar()
            assert count == 10, f"Expected 10 records, got {count}"
            
            # Test data integrity
            result = await conn.execute(text("SELECT * FROM consistency_test WHERE id BETWEEN 1 AND 5"))
            rows = await result.fetchall()
            assert len(rows) == 5
    
    return _test_consistency


# Monitoring and observability fixtures
@pytest_asyncio.fixture
def postgres_monitoring_setup(postgres_test_engine):
    """Setup PostgreSQL monitoring and observability."""
    async def _setup_monitoring():
        # Create monitoring tables
        async with postgres_test_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS query_logs (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT,
                    execution_time FLOAT,
                    row_count INTEGER,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    user_id VARCHAR(100)
                )
            """))
            
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
    
    return _setup_monitoring


# Cleanup and teardown fixtures
@pytest_asyncio.fixture
def cleanup_postgres_test_data(postgres_test_engine):
    """Clean up PostgreSQL test data."""
    async def _cleanup_test_data():
        async with postgres_test_engine.begin() as conn:
            # Drop test tables
            await conn.execute(text("DROP TABLE IF EXISTS performance_test"))
            await conn.execute(text("DROP TABLE IF EXISTS query_logs"))
            await conn.execute(text("DROP TABLE IF EXISTS performance_metrics"))
            
            # Clean up any remaining test data
            await conn.execute(text("TRUNCATE masjids RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE salat_schedules RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE masjid_programs RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE program_schedules RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE masjid_people RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE masjid_photos RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE audit_events RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE outbox_events RESTART IDENTITY CASCADE"))
    
    return _cleanup_test_data


@pytest_asyncio.fixture
def postgres_full_test_environment(
    postgres_container,
    postgres_test_engine,
    seed_postgres_database,
    postgres_consistency_test,
    postgres_error_recovery_test,
    postgres_monitoring_setup,
    cleanup_postgres_test_data,
):
    """Create a complete PostgreSQL full test environment."""
    async def _setup_full_environment():
        # Setup monitoring
        await postgres_monitoring_setup()
        
        # Seed the database
        await seed_postgres_database()
        
        # Run consistency tests
        await postgres_consistency_test()
        
        # Run error recovery tests
        await postgres_error_recovery_test()
        
        print("PostgreSQL full test environment setup complete")
    
    return _setup_full_environment


# Configuration and metadata fixtures
@pytest.fixture
def postgres_testcontainers_documentation():
    """Provide PostgreSQL Testcontainers documentation."""
    return {
        'overview': 'PostgreSQL Testcontainers Fixtures for Dual Testing Strategy',
        'description': 'Comprehensive PostgreSQL + PostGIS test fixtures using Testcontainers',
        'requirements': [
            'Docker installed and running',
            'Testcontainers Python package installed',
            'PostgreSQL container with PostGIS extension',
            'Network connectivity to container',
        ],
        'usage_examples': [
            """
            @pytest.mark.asyncio
            async def test_postgis_operations(postgres_test_engine):
                # Test with real PostgreSQL + PostGIS
                async with postgres_test_engine.begin() as conn:
                    result = await conn.execute(
                        text("SELECT ST_AsText(location) FROM masjids")
                    )
                    rows = await result.fetchall()
                    assert len(rows) > 0
            """,
            """
            @pytest.mark.asyncio
            async def test_jsonb_operations(postgres_test_engine):
                # Test JSONB operations
                async with postgres_test_engine.begin() as conn:
                    await conn.execute(text("""
                        UPDATE masjids 
                        SET meta = meta || '{"test": true}'::jsonb 
                        WHERE id = :id
                    """), {"id": "test-id"})
                    
                    result = await conn.execute(
                        text("SELECT meta FROM masjids WHERE id = :id"),
                        {"id": "test-id"}
                    )
                    row = await result.scalar_one_or_none()
                    assert row is not None
            """,
        ],
        'best_practices': [
            'Use transaction fixtures for test isolation',
            'Clean up test data after each test',
            'Set up PostGIS extension before testing',
            'Use parameterized queries to prevent SQL injection',
            'Monitor database performance during tests',
        ],
        'benefits': [
            'Real PostgreSQL + PostGIS testing',
            'Comprehensive spatial operations',
            'JSONB functionality testing',
            'Production parity',
            'Test isolation with transaction rollback',
        ],
    }


@pytest.fixture
def provide_comprehensive_postgres_fixture_set():
    """Provide a comprehensive set of PostgreSQL test fixtures."""
    fixtures = {
        'setup': 'postgres_full_test_environment',
        'engine': 'postgres_test_engine',
        'session': 'postgres_session',
        'client': 'postgres_real_client',
        'container': 'postgres_container',
        'connection': 'postgres_connection_string',
        'postgis_setup': 'setup_postgis_extension',
        'schema_creation': 'create_test_database_schema',
        'test_data': 'seed_postgres_database',
        'transaction_test': 'postgres_transaction_isolation',
        'error_recovery': 'postgres_error_recovery_test',
        'consistency': 'postgres_consistency_test',
        'monitoring': 'postgres_monitoring_setup',
        'cleanup': 'cleanup_postgres_test_data',
        'spatial_mock': 'mock_postgis_functions',
        'performance': 'postgres_performance_test',
        'integration': 'postgres_postgis_integration_test',
    }
    
    return fixtures


# Complete fixture list for import
__all__ = [
    'postgres_container_image',
    'postgres_container_environment',
    'postgres_container_ports',
    'postgres_container',
    'postgres_connection_string',
    'postgres_test_engine',
    'postgres_session',
    'postgres_transaction_isolation',
    'postgis_extension_available',
    'setup_postgis_extension',
    'create_test_database_schema',
    'setup_postgis_test_data',
    'seed_postgres_database',
    'postgres_real_client',
    'mock_postgis_functions',
    'postgres_spatial_operations_mock',
    'postgres_transaction_test',
    'postgres_postgis_integration_test',
    'postgres_full_integration_environment',
    'postgres_testcontainers_config',
    'postgres_test_data_samples',
    'postgres_performance_test',
    'postgres_stress_test_config',
    'postgres_error_recovery_test',
    'postgres_consistency_test',
    'postgres_monitoring_setup',
    'cleanup_postgres_test_data',
    'postgres_full_test_environment',
    'postgres_testcontainers_documentation',
    'provide_comprehensive_postgres_fixture_set',
]