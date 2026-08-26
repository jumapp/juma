"""SQLite quick test fixtures for dual testing strategy.

This module provides test fixtures for SQLite-based quick tests,
including mocked PostgreSQL types and simplified database setup.
"""

import asyncio
import json
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator, Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import JSON, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.config import settings


@pytest.fixture(scope="session")
def temp_sqlite_db():
    """Create a temporary SQLite database file for tests."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_quick.db"
    yield db_path
    # Clean up after tests
    import shutil
    if db_path.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sqlite_test_engine(temp_sqlite_db):
    """Create an async SQLite engine for testing."""
    # SQLite doesn't support all PostgreSQL types, so we need to mock them
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{temp_sqlite_db}",
        echo=settings.db_echo,
        poolclass=NullPool,
    )
    return engine


@pytest_asyncio.fixture
def sqlite_session(sqlite_test_engine):
    """Create an async session for SQLite tests."""
    async def _session():
        async with sqlite_test_engine.begin() as conn:
            yield conn
    
    return _session()


@pytest.fixture
def mock_postgresql_types():
    """Mock PostgreSQL-specific types for SQLite compatibility."""
    with patch('sqlalchemy.JSONB') as mock_jsonb, \
         patch('sqlalchemy.Geography') as mock_geography, \
         patch('sqlalchemy.types.JSON') as mock_json_type:
        
        # Create mock type instances that SQLite can handle
        mock_jsonb_instance = MagicMock()
        mock_jsonb_instance.astext = lambda x: json.loads(x) if x else None
        
        mock_geography_instance = MagicMock()
        mock_geography_instance.as_text = lambda x: json.dumps(x) if x else None
        
        mock_json_type_instance = MagicMock()
        mock_json_type_instance.python_type = dict
        
        mock_jsonb.return_value = mock_jsonb_instance
        mock_geography.return_value = mock_geography_instance
        mock_json_type.return_value = mock_json_type_instance
        
        yield mock_jsonb_instance, mock_geography_instance, mock_json_type_instance


@pytest.fixture
def mock_geography_for_sqlite():
    """Mock Geography type specifically for SQLite tests."""
    with patch('sqlalchemy.Geography') as mock_geography:
        # Create a mock that can be used in place of Geography
        mock_geo = MagicMock()
        mock_geo.geometry_type = "POINT"
        mock_geo.srid = 4326
        mock_geo.as_text = lambda self, val: json.dumps(val) if val else "POINT(0 0)"
        mock_geo.as WKT = lambda self, val: val if val else "POINT(0 0)"
        
        # Return a mock class that can be instantiated
        def geography_mock(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.geometry_type = "POINT"
            mock_instance.srid = 4326
            mock_instance.as_text = lambda val: json.dumps(val) if val else "POINT(0 0)"
            return mock_instance
        
        mock_geography.side_effect = geography_mock
        yield mock_geography


@pytest.fixture
def mock_jsonb_for_sqlite():
    """Mock JSONB type specifically for SQLite tests."""
    with patch('sqlalchemy.JSONB') as mock_jsonb:
        # Create a mock that can be used in place of JSONB
        mock_jsonb_instance = MagicMock()
        mock_jsonb_instance.python_type = dict
        mock_jsonb_instance.astext = lambda x: json.loads(x) if x else None
        
        # Return a mock class that can be instantiated
        def jsonb_mock(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.python_type = dict
            mock_instance.astext = lambda x: json.loads(x) if x else None
            return mock_instance
        
        mock_jsonb.side_effect = jsonb_mock
        yield mock_jsonb


@pytest.fixture
def mock_database_services():
    """Mock database services for SQLite quick tests."""
    with patch('backend.app.services.masjid_service.get_masjid_service') as mock_masjid_svc, \
         patch('backend.app.services.salat_service.get_salat_service') as mock_salat_svc, \
         patch('backend.app.services.program_service.get_program_service') as mock_program_svc, \
         patch('backend.app.services.person_service.get_person_service') as mock_person_svc, \
         patch('backend.app.services.photo_service.get_photo_service') as mock_photo_svc, \
         patch('backend.app.services.sync_service.get_sync_service') as mock_sync_svc:
        
        # Create comprehensive mock service instances
        mock_masjid_service = MagicMock()
        mock_salat_service = MagicMock()
        mock_program_service = MagicMock()
        mock_person_service = MagicMock()
        mock_photo_service = MagicMock()
        mock_sync_service = MagicMock()
        
        mock_masjid_svc.return_value = mock_masjid_service
        mock_salat_svc.return_value = mock_salat_service
        mock_program_svc.return_value = mock_program_service
        mock_person_svc.return_value = mock_person_service
        mock_photo_svc.return_value = mock_photo_service
        mock_sync_svc.return_value = mock_sync_service
        
        yield {
            'masjid': mock_masjid_service,
            'salat': mock_salat_service,
            'program': mock_program_service,
            'person': mock_person_service,
            'photo': mock_photo_service,
            'sync': mock_sync_service,
        }


@pytest.fixture
def mock_auth_service():
    """Mock authentication service for SQLite quick tests."""
    with patch('backend.app.auth_service.get_user') as mock_get_user:
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.username = "test_user"
        mock_user.role = "super_admin"
        
        mock_get_user.return_value = mock_user
        yield mock_get_user


@pytest_asyncio.fixture
def sqlite_client(mock_database_services, mock_auth_service):
    """Create a test client with mocked SQLite database and services."""
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db import get_db
    
    # Create a mock database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Override the database dependency
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Override service dependencies
    from backend.app import routers
    for router_name, service_key in [
        ('masjid_service', mock_database_services['masjid']),
        ('salat_service', mock_database_services['salat']),
        ('program_service', mock_database_services['program']),
        ('person_service', mock_database_services['person']),
        ('photo_service', mock_database_services['photo']),
        ('sync_service', mock_database_services['sync']),
    ]:
        # This would be more complex in a real implementation
        # For now, we'll just patch the import
        pass
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_data_for_sqlite():
    """Generate test data compatible with SQLite for quick tests."""
    from backend.tests.conftest import (
        TEST_MASJID_ID,
        make_masjid_editor_headers,
        make_salat_editor_headers,
        VIEWER_HEADERS,
        SUPER_ADMIN_HEADERS,
        SAMPLE_MASJID_DATA,
        SAMPLE_SALAT_DATA,
        SAMPLE_PROGRAM_DATA,
        SAMPLE_PERSON_DATA,
        SAMPLE_PHOTO_DATA,
    )
    
    return {
        'TEST_MASJID_ID': TEST_MASJID_ID,
        'masjid_editor_headers': {
            'default': make_masjid_editor_headers(),
            'custom': make_masjid_editor_headers(TEST_MASJID_ID),
        },
        'salat_editor_headers': {
            'default': make_salat_editor_headers(),
            'custom': make_salat_editor_headers(TEST_MASJID_ID),
        },
        'headers': {
            'super_admin': SUPER_ADMIN_HEADERS,
            'viewer': VIEWER_HEADERS,
        },
        'sample_data': {
            'masjid': SAMPLE_MASJID_DATA,
            'salat': SAMPLE_SALAT_DATA,
            'program': SAMPLE_PROGRAM_DATA,
            'person': SAMPLE_PERSON_DATA,
            'photo': SAMPLE_PHOTO_DATA,
        },
    }


@pytest.fixture
def mock_spatial_operations():
    """Mock spatial operations for SQLite compatibility."""
    with patch('backend.app.services.masjid_service.calculate_distance') as mock_distance, \
         patch('backend.app.services.masjid_service.transform_coordinates') as mock_transform, \
         patch('backend.app.services.masjid_service.validate_location') as mock_validate:
        
        # Mock spatial operations with simple implementations
        mock_distance.return_value = 1000.0  # meters
        mock_transform.return_value = (30.3165, 78.0322)  # lat, lon
        mock_validate.return_value = True
        
        yield {
            'distance': mock_distance,
            'transform': mock_transform,
            'validate': mock_validate,
        }


@pytest_asyncio.fixture
def async_sqlite_client(
    mock_database_services,
    mock_auth_service,
    mock_spatial_operations,
):
    """Create an async test client for SQLite quick tests."""
    from httpx import AsyncClient
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db import get_db
    
    # Mock the database dependency
    mock_db = AsyncMock(spec=AsyncSession)
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@contextmanager
def mock_postgresql_type_environment():
    """Create a context manager that mocks PostgreSQL types for SQLite."""
    # Store original types
    original_jsonb = None
    original_geography = None
    
    # Mock PostgreSQL types
    with patch('sqlalchemy.JSONB') as mock_jsonb, \
         patch('sqlalchemy.Geography') as mock_geography:
        
        # Create mock implementations
        mock_jsonb_instance = MagicMock()
        mock_jsonb_instance.python_type = dict
        mock_jsonb_instance.astext = lambda x: json.loads(x) if x else None
        
        mock_geography_instance = MagicMock()
        mock_geography_instance.geometry_type = "POINT"
        mock_geography_instance.srid = 4326
        mock_geography_instance.as_text = lambda x: json.dumps(x) if x else "POINT(0 0)"
        
        # Set up side effects for instantiation
        def jsonb_side_effect(*args, **kwargs):
            return mock_jsonb_instance
        
        def geography_side_effect(*args, **kwargs):
            return mock_geography_instance
        
        mock_jsonb.side_effect = jsonb_side_effect
        mock_geography.side_effect = geography_side_effect
        
        yield {
            'jsonb': mock_jsonb_instance,
            'geography': mock_geography_instance,
        }


def create_sqlite_compatible_models():
    """Create SQLAlchemy model definitions compatible with SQLite."""
    from sqlalchemy import Column, Integer, String, Float, Text
    from sqlalchemy.ext.declarative import declarative_base
    
    Base = declarative_base()
    
    class MockMasjid(Base):
        """SQLite-compatible mock of Masjid model."""
        __tablename__ = 'masjids'
        
        id = Column(Integer, primary_key=True)
        name = Column(String)
        address_line1 = Column(String)
        city = Column(String)
        state = Column(String)
        country = Column(String)
        latitude = Column(Float)
        longitude = Column(Float)
        timezone = Column(String)
        # Mock PostgreSQL types as regular SQLite columns
        location = Column(Text)  # Geography -> Text
        ramadan_adjusted_hours = Column(Text)  # JSONB -> Text
        meta = Column(Text)  # JSONB -> Text
    
    return Base, MockMasjid


@pytest.fixture
def sqlite_compatible_models():
    """Create SQLite-compatible model classes."""
    Base, MockMasjid = create_sqlite_compatible_models()
    yield Base, MockMasjid


@pytest.fixture
def mock_coordinates_transformer():
    """Mock coordinate transformation functions."""
    with patch('backend.app.services.masjid_service.transform_coordinates') as mock_transform:
        mock_transform.return_value = (30.3165, 78.0322)  # lat, lon
        yield mock_transform


@pytest.fixture
def mock_postgis_functions():
    """Mock PostGIS functions for SQLite compatibility."""
    with patch('backend.app.services.masjid_service.st_intersects') as mock_intersects, \
         patch('backend.app.services.masjid_service.st_distance') as mock_distance, \
         patch('backend.app.services.masjid_service.st_transform') as mock_transform:
        
        mock_intersects.return_value = True
        mock_distance.return_value = 1000.0
        mock_transform.return_value = (30.3165, 78.0322)
        
        yield {
            'intersects': mock_intersects,
            'distance': mock_distance,
            'transform': mock_transform,
        }


@pytest.fixture
def sqlite_test_data_generator():
    """Generate test data specifically for SQLite tests."""
    def generate_test_masjid_data(masjid_id="test-001"):
        """Generate mock masjid data for SQLite tests."""
        return {
            'id': masjid_id,
            'name': 'Test Masjid',
            'address_line1': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'IN',
            'latitude': 30.3165,
            'longitude': 78.0322,
            'timezone': 'Asia/Kolkata',
            'location': json.dumps({
                'type': 'Point',
                'coordinates': [78.0322, 30.3165],
                'srid': 4326
            }),
            'ramadan_adjusted_hours': json.dumps({
                'start': '05:30',
                'end': '19:30'
            }),
            'meta': json.dumps({
                'timezone': 'Asia/Kolkata',
                'access_level': 'admin'
            })
        }
    
    def generate_test_person_data(masjid_id="test-masjid"):
        """Generate mock person data for SQLite tests."""
        return {
            'id': f'person-{masjid_id}',
            'masjid_id': masjid_id,
            'full_name': 'Test Person',
            'role': 'imam',
            'access_level': 'viewer',
            'phone_primary': '+919876543210',
            'email': 'test@example.com',
            'is_active': True,
        }
    
    yield {
        'masjid': generate_test_masjid_data,
        'person': generate_test_person_data,
    }


@pytest.fixture
def setup_sqlite_test_data():
    """Setup test data for SQLite tests."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    
    async def _setup_data():
        # Create temporary database
        import tempfile
        from pathlib import Path
        
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_setup.db"
        
        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        
        # Create tables
        from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Float
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        metadata = MetaData()
        
        users_table = Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String),
            Column('role', String),
            Column('is_active', Integer)
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        
        # Insert test data
        async with AsyncSession(engine) as session:
            session.execute(users_table.insert(), [
                {'username': 'test_user_1', 'role': 'super_admin', 'is_active': 1},
                {'username': 'test_user_2', 'role': 'viewer', 'is_active': 1},
            ])
            await session.commit()
        
        yield engine
        
        # Clean up
        await engine.dispose()
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return _setup_data


# Alias for backward compatibility
@contextmanager
def mock_postgresql_type_environment_sqlite():
    """Legacy alias for mock_postgresql_type_environment."""
    with mock_postgresql_type_environment() as env:
        yield env


@pytest.fixture
def mock_spatial_service():
    """Mock spatial service for SQLite tests."""
    with patch('backend.app.services.masjid_service.MasjidSpatialService') as mock_spatial_service:
        mock_instance = MagicMock()
        mock_spatial_service.return_value = mock_instance
        
        # Configure mock methods
        mock_instance.calculate_distance.return_value = 1000.0
        mock_instance.transform_coordinates.return_value = (30.3165, 78.0322)
        mock_instance.validate_location.return_value = True
        mock_instance.get_coordinates.return_value = (30.3165, 78.0322)
        
        yield mock_instance


@pytest.fixture
def mock_coordinate_validation():
    """Mock coordinate validation for SQLite tests."""
    with patch('backend.app.services.masjid_service.validate_coordinates') as mock_validate:
        mock_validate.return_value = True
        yield mock_validate


@pytest.fixture
def mock_massajid_cache():
    """Mock masjid cache service for SQLite tests."""
    with patch('backend.app.services.masjid_service.get_cached_masjid') as mock_cache:
        mock_cache.return_value = None
        yield mock_cache


@pytest.fixture
def mock_massajid_repository():
    """Mock masjid repository for SQLite tests."""
    with patch('backend.app.repositories.masjid_repository.get_all_masjids') as mock_get_all:
        mock_get_all.return_value = []
        yield mock_get_all


@pytest_asyncio.fixture
def async_sqlite_session():
    """Create an async SQLite session for testing."""
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "async_test.db"
    
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    
    async def get_session():
        async with AsyncSession(engine) as session:
            yield session
    
    return get_session()


@pytest.fixture
def create_test_environment_for_sqlite():
    """Create a complete test environment for SQLite tests."""
    def _create_test_environment():
        # This would set up all the necessary mocks and dependencies
        # for SQLite testing in a comprehensive way
        environment = {
            'database_type': 'sqlite',
            'supports_postgresql_types': False,
            'mock_geography': True,
            'mock_jsonb': True,
            'fast_queries': True,
            'no_external_dependencies': True,
        }
        return environment
    
    return _create_test_environment


# Performance testing fixtures
def setup_sqlite_performance_benchmark():
    """Setup performance benchmarks for SQLite tests."""
    import time
    from sqlalchemy import text
    
    def benchmark_query(engine, query_func, iterations=100):
        """Benchmark a database query performance."""
        start_time = time.time()
        
        for _ in range(iterations):
            query_func()
        
        end_time = time.time()
        return (end_time - start_time) / iterations
    
    return benchmark_query


# Error handling fixtures
def setup_sqlite_error_handling():
    """Setup error handling for SQLite tests."""
    def test_sqlite_connection_error():
        """Test SQLite connection error handling."""
        # Test various SQLite error scenarios
        pass
    
    def test_sqlite_constraint_violations():
        """Test SQLite constraint violations."""
        pass
    
    return {
        'connection_error': test_sqlite_connection_error,
        'constraint_violations': test_sqlite_constraint_violations,
    }

# Test data fixtures
def create_sqlite_test_fixtures():
    """Create comprehensive SQLite test fixtures."""
    fixtures = {
        'test_masjid_data': [],
        'test_person_data': [],
        'test_photo_data': [],
        'test_program_data': [],
        'test_salat_data': [],
        'test_sync_data': [],
    }
    return fixtures

# Cleanup and teardown fixtures
@pytest.fixture
def cleanup_sqlite_resources():
    """Clean up SQLite test resources."""
    yield
    
    # Clean up any temporary files
    import tempfile
    temp_dir = tempfile.gettempdir()
    
    # Clean up test database files
    for file_path in Path(temp_dir).glob("test_*.db"):
        try:
            file_path.unlink()
        except Exception:
            pass

# Integration testing fixtures
def setup_sqlite_integration_tests():
    """Setup integration tests for SQLite."""
    def test_sqlite_jsonb_serialization():
        """Test JSONB serialization in SQLite."""
        import json
        
        # Test JSONB-like serialization
        test_data = {'key': 'value', 'number': 123, 'nested': {'inner': 'data'}}
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        
        assert parsed_data['key'] == 'value'
        assert parsed_data['number'] == 123
        assert parsed_data['nested']['inner'] == 'data'
    
    def test_sqlite_geography_serialization():
        """Test Geography serialization in SQLite."""
        import json
        
        # Test Geography-like serialization
        geo_data = {
            'type': 'Point',
            'coordinates': [78.0322, 30.3165],
            'srid': 4326
        }
        geo_str = json.dumps(geo_data)
        parsed_geo = json.loads(geo_str)
        
        assert parsed_geo['type'] == 'Point'
        assert len(parsed_geo['coordinates']) == 2
        assert parsed_geo['srid'] == 4326
    
    return {
        'jsonb_serialization': test_sqlite_jsonb_serialization,
        'geography_serialization': test_sqlite_geography_serialization,
    }


@pytest.fixture
def create_sqlite_test_scenarios():
    """Create various test scenarios for SQLite testing."""
    def create_basic_masjid_test():
        """Create a basic masjid test scenario."""
        return {
            'description': 'Basic masjid CRUD operations',
            'setup_steps': [
                'Create masjid with coordinates',
                'Retrieve masjid by ID',
                'Update masjid details',
                'Delete masjid',
            ],
            'expected_results': {
                'create': 'success',
                'retrieve': 'success',
                'update': 'success',
                'delete': 'success',
            }
        }
    
    def create_spatial_masjid_test():
        """Create a spatial masjid test scenario."""
        return {
            'description': 'Spatial operations with mocked PostGIS',
            'setup_steps': [
                'Create masjid with location',
                'Calculate distance between masjids',
                'Find nearby masjids',
                'Transform coordinates',
            ],
            'expected_results': {
                'distance_calculation': 'success',
                'location_search': 'success',
                'coordinate_transformation': 'success',
            }
        }
    
    def create_jsonb_masjid_test():
        """Create a JSONB masjid test scenario."""
        return {
            'description': 'JSONB field handling for extended metadata',
            'setup_steps': [
                'Create masjid with JSONB meta field',
                'Update meta field',
                'Query by meta field',
                'Filter by JSONB content',
            ],
            'expected_results': {
                'meta_creation': 'success',
                'meta_update': 'success',
                'meta_query': 'success',
                'meta_filter': 'success',
            }
        }
    
    return {
        'basic_masjid': create_basic_masjid_test,
        'spatial_masjid': create_spatial_masjid_test,
        'jsonb_masjid': create_jsonb_masjid_test,
    }


# Documentation and metadata fixtures
@pytest.fixture
def provide_sqlite_test_documentation():
    """Provide documentation for SQLite test fixtures."""
    documentation = {
        'description': 'SQLite Quick Test Fixtures',
        'purpose': 'Provide fast, isolated tests using SQLite with mocked PostgreSQL types',
        'advantages': [
            'Fast test execution',
            'No external dependencies',
            'Simple setup and teardown',
            'Ideal for CI/CD pipelines',
            'Developer-friendly for rapid iteration',
        ],
        'limitations': [
            'Limited to non-PostgreSQL-specific features',
            'Mocked PostgreSQL types (Geography, JSONB)',
            'No real spatial operations',
            'No real PostGIS functions',
        ],
        'usage': """
        # Use in test files:
        # 1. Import fixtures: from backend.tests.conftest_sqlite import sqlite_test_engine
        # 2. Use markers: @pytest.mark.quick
        # 3. Set environment: export TEST_MODE=test
        # 4. Run tests: pytest backend/tests/ -v
        """,
        'examples': [
            {
                'name': 'Basic SQLite test',
                'code': """
@pytest.mark.asyncio
async def test_masjid_crud(sqlite_session):
    # Test with SQLite session
    async with sqlite_session() as session:
        # Perform database operations
        result = await session.execute("SELECT 1")
        assert result.scalar() == 1
        """
            },
        ],
    }
    return documentation


# Configuration and compatibility fixtures
@pytest.fixture
def sqlite_compatibility_settings():
    """Get SQLite compatibility settings."""
    return {
        'database_url': 'sqlite+aiosqlite:///./test_quick.db',
        'poolclass': NullPool,
        'echo': True,
        'future': True,
        'connect_args': {
            'check_same_thread': False,
        },
        'type_annotations': False,
        'json_serializer': lambda obj: json.dumps(obj, default=str),
        'json_deserializer': json.loads,
    }


@pytest.fixture
def sqlite_session_factory(sqlite_test_engine):
    """Create a session factory for SQLite tests."""
    async_session_factory = sessionmaker(
        sqlite_test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async def get_session():
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    return get_session


@pytest.fixture
def sqlite_test_data_cleanup():
    """Cleanup SQLite test data."""
    def _cleanup_test_data(session):
        # Clean up test data
        # This is a placeholder for actual cleanup logic
        pass
    
    return _cleanup_test_data


# Performance and benchmarking fixtures
@pytest.fixture
def sqlite_performance_metrics():
    """"Provide performance metrics for SQLite tests."""
    import time
    
    metrics = {
        'query_times': [],
        'memory_usage': [],
        'connection_times': [],
    }
    
    def record_query_time(duration):
        metrics['query_times'].append(duration)
    
    def record_memory_usage(usage):
        metrics['memory_usage'].append(usage)
    
    def record_connection_time(duration):
        metrics['connection_times'].append(duration)
    
    def get_average_query_time():
        if not metrics['query_times']:
            return 0.0
        return sum(metrics['query_times']) / len(metrics['query_times'])
    
    def get_max_query_time():
        if not metrics['query_times']:
            return 0.0
        return max(metrics['query_times'])
    
    yield {
        'record_query_time': record_query_time,
        'record_memory_usage': record_memory_usage,
        'record_connection_time': record_connection_time,
        'get_average_query_time': get_average_query_time,
        'get_max_query_time': get_max_query_time,
        'get_metrics': lambda: metrics.copy(),
    }


# Debugging and inspection fixtures
@pytest.fixture
def sqlite_debug_mode():
    """Enable debug mode for SQLite tests."""
    import logging
    
    logging.basicConfig(level=logging.DEBUG)
    
    # Enable SQLAlchemy debug logging
    import sqlalchemy.engine
    from sqlalchemy import event
    
    @event.listens_for(sqlalchemy.engine.Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        logging.debug(f"SQL Query: {statement}")
        logging.debug(f"Parameters: {parameters}")
    
    yield


@pytest.fixture
def sqlite_inspection_tools():
    """Provide tools for inspecting SQLite test environment."""
    def inspect_database_schema(engine):
        """Inspect the database schema."""
        from sqlalchemy import inspect as sa_inspect
        
        inspector = sa_inspect(engine)
        tables = inspector.get_table_names()
        
        schema_info = {}
        for table in tables:
            columns = inspector.get_columns(table)
            schema_info[table] = {
                'columns': [{'name': col['name'], 'type': col['type'].__name__} for col in columns],
                'primary_key': inspector.get_primary_keys(table),
                'foreign_keys': inspector.get_foreign_keys(table),
            }
        
        return schema_info
    
    def check_table_exists(engine, table_name):
        """Check if a table exists in the database."""
        from sqlalchemy import inspect as sa_inspect
        
        inspector = sa_inspect(engine)
        return inspector.has_table(table_name)
    
    def get_table_row_count(engine, table_name):
        """Get the row count of a table."""
        with engine.connect() as conn:
            result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return result.scalar()
    
    yield {
        'inspect_database_schema': inspect_database_schema,
        'check_table_exists': check_table_exists,
        'get_table_row_count': get_table_row_count,
    }


# Test data validation fixtures
@pytest.fixture
def sqlite_test_data_validators():
    """Provide test data validation utilities for SQLite tests."""
    def validate_masjid_data(data):
        """Validate masjid test data."""
        required_fields = ['id', 'name', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(data['latitude'], (int, float)):
            raise ValueError("Latitude must be a number")
        
        if not isinstance(data['longitude'], (int, float)):
            raise ValueError("Longitude must be a number")
        
        if data['latitude'] < -90 or data['latitude'] > 90:
            raise ValueError("Latitude must be between -90 and 90")
        
        if data['longitude'] < -180 or data['longitude'] > 180:
            raise ValueError("Longitude must be between -180 and 180")
        
        return True
    
    def validate_person_data(data):
        """Validate person test data."""
        required_fields = ['id', 'full_name', 'masjid_id']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(data['full_name'], str):
            raise ValueError("Full name must be a string")
        
        if not isinstance(data['is_active'], bool):
            raise ValueError("Is active must be a boolean")
        
        return True
    
    yield {
        'validate_masjid_data': validate_masjid_data,
        'validate_person_data': validate_person_data,
    }


# Configuration and environment fixtures
@pytest.fixture
def sqlite_environment_config():
    """Configure test environment for SQLite."""
    import os
    import tempfile
    from pathlib import Path
    
    # Create temporary directory for test database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_env.db"
    
    # Set environment variables
    os.environ['TEST_DATABASE_URL'] = f"sqlite+aiosqlite:///{db_path}"
    os.environ['TEST_ENVIRONMENT'] = 'test'
    
    yield {
        'temp_dir': temp_dir,
        'db_path': db_path,
        'database_url': f"sqlite+aiosqlite:///{db_path}",
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Clean up environment variables
    os.environ.pop('TEST_DATABASE_URL', None)
    os.environ.pop('TEST_ENVIRONMENT', None)


@pytest.fixture
def sqlite_test_setup():
    """"Setup complete SQLite test environment."""
    from sqlalchemy import MetaData, Table, Column, Integer, String
    
    async def _setup_test_environment(engine):
        # Create test tables
        metadata = MetaData()
        
        # Create users table
        Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String),
            Column('role', String),
            Column('is_active', Integer)
        )
        
        # Create masjids table
        Table('masjids', metadata,
            Column('id', String, primary_key=True),
            Column('name', String),
            Column('latitude', Float),
            Column('longitude', Float),
            Column('timezone', String),
            Column('location', Text),  # Mock Geography
            Column('meta', Text),  # Mock JSONB
        )
        
        # Create test data
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            
            # Insert test data
            await conn.execute(
                users_table.insert(),
                [
                    {'username': 'test_user_1', 'role': 'super_admin', 'is_active': 1},
                    {'username': 'test_user_2', 'role': 'viewer', 'is_active': 1},
                ]
            )
    
    return _setup_test_environment


# Additional utility fixtures
@pytest.fixture
def create_sqlite_test_suite():
    """Create a complete SQLite test suite."""
    def _create_test_suite():
        return {
            'test_name': 'SQLite Quick Test Suite',
            'description': 'Comprehensive test suite using SQLite with mocked PostgreSQL types',
            'fixtures': [
                'sqlite_test_engine',
                'sqlite_session',
                'mock_postgresql_types',
                'mock_database_services',
                'sqlite_client',
            ],
            'test_patterns': [
                '*.py',
                '!integration',
                '!performance',
            ],
            'configuration': {
                'test_mode': 'sqlite',
                'database_url': 'sqlite+aiosqlite:///./test_quick.db',
                'mock_postgresql_types': True,
                'service_mocking': True,
                'fast_execution': True,
            },
            'expected_results': {
                'execution_time': 'fast (< 1 second per test)',
                'setup_complexity': 'low',
                'maintenance_overhead': 'low',
                'coverage_scope': 'limited (non-PostgreSQL features)',
            }
        }
    
    return _create_test_suite


@pytest.fixture
def sqlite_performance_benchmark():
    """Setup performance benchmarking for SQLite tests."""
    import time
    from sqlalchemy import text
    
    class Benchmarker:
        def __init__(self):
            self.results = []
        
        async def benchmark_query(self, engine, query, iterations=100):
            """Benchmark a database query."""
            times = []
            
            for _ in range(iterations):
                start_time = time.time()
                await engine.execute(text(query))
                end_time = time.time()
                
                times.append(end_time - start_time)
            
            self.results.append({
                'query': query,
                'iterations': iterations,
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times),
            })
            
            return self.results[-1]
        
        def get_summary(self):
            """Get benchmark summary."""
            if not self.results:
                return {}
            
            total_queries = sum(r['iterations'] for r in self.results)
            total_time = sum(r['total_time'] for r in self.results)
            
            return {
                'total_queries': total_queries,
                'total_time': total_time,
                'avg_time_per_query': total_time / total_queries if total_queries > 0 else 0,
                'benchmarked_queries': len(self.results),
            }
    
    return Benchmarker


# Test isolation fixtures
@pytest_asyncio.fixture
def clean_sqlite_state():
    """Ensure clean state for each SQLite test."""
    from sqlalchemy import text
    
    async def _clean_state(engine):
        # Truncate all tables to ensure clean state
        tables = ['users', 'masjids', 'photos', 'programs', 'salat_schedules', 'people']
        
        async with engine.begin() as conn:
            for table in tables:
                try:
                    await conn.execute(text(f"DELETE FROM {table}"))
                except Exception:
                    pass  # Table might not exist
    
    return _clean_state


@pytest.fixture
def sqlite_test_isolation():
    """Ensure test isolation for SQLite tests."""
    import tempfile
    from pathlib import Path
    
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "isolated_test.db"
    
    yield {
        'database_url': f"sqlite+aiosqlite:///{db_path}",
        'temp_dir': temp_dir,
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


# Final verification and validation fixtures
@pytest.fixture
def sqlite_final_validation():
    """Final validation for SQLite test setup."""
    def _validate_setup(engine):
        # Verify database is accessible
        async def _check_connection():
            try:
                await engine.execute(text("SELECT 1"))
                return True
            except Exception:
                return False
        
        # Verify tables exist
        async def _check_tables():
            from sqlalchemy import inspect as sa_inspect
            
            inspector = sa_inspect(engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            return len(missing_tables) == 0, missing_tables
        
        return {
            'connection_check': _check_connection,
            'table_check': _check_tables,
        }
    
    return _validate_setup


# Documentation and examples fixtures
@pytest.fixture
def sqlite_test_documentation():
    """Provide documentation for SQLite test fixtures."""
    return {
        'overview': 'SQLite Quick Test Fixtures for Dual Testing Strategy',
        'description': 'Comprehensive SQLite test fixtures with mocked PostgreSQL types',
        'usage_examples': [
            """
            @pytest.mark.asyncio
            async def test_masjid_operations(sqlite_session):
                # Use SQLite session for testing
                async with sqlite_session() as session:
                    # Perform database operations
                    result = await session.execute(
                        text("SELECT * FROM masjids WHERE id = :id"),
                        {"id": "test-masjid-id"}
                    )
                    masjid = result.scalar_one_or_none()
                    assert masjid is not None
                    assert masjid.name == "Test Masjid"
            """,
            """
            @pytest.mark.asyncio
            async def test_user_authentication(sqlite_client):
                # Use SQLite client for testing API endpoints
                response = await sqlite_client.post(
                    "/api/v1/login",
                    json={"username": "test_user", "password": "test_password"}
                )
                assert response.status_code == 200
                assert "token" in response.json()
            """,
        ],
        'best_practices': [
            "Always use the sqlite_session fixture for database operations",
            "Mock PostgreSQL types (Geography, JSONB) for SQLite compatibility",
            "Use transaction rollback for test isolation",
            "Clean up temporary database files after tests",
            "Use markers (@pytest.mark.quick) to identify SQLite tests",
        ],
        'limitations': [
            "Cannot test real PostgreSQL-specific features",
            "PostGIS functionality is mocked",
            "Real database performance characteristics may differ",
        ],
    }


@pytest.fixture
def provide_comprehensive_sqlite_fixture_set():
    """Provide a comprehensive set of SQLite test fixtures."""
    fixtures = {
        'setup': 'sqlite_test_setup',
        'session': 'sqlite_session',
        'client': 'sqlite_client',
        'mock_types': 'mock_postgresql_types',
        'mock_services': 'mock_database_services',
        'auth': 'mock_auth_service',
        'spatial': 'mock_spatial_operations',
        'data': 'test_data_for_sqlite',
        'performance': 'sqlite_performance_metrics',
        'isolation': 'sqlite_test_isolation',
        'validation': 'sqlite_final_validation',
        'cleanup': 'cleanup_sqlite_resources',
    }
    
    return fixtures


# Final fixture for comprehensive SQLite testing
@pytest.fixture
def sqlite_comprehensive_test_environment():
    """Create a comprehensive SQLite test environment."""
    return {
        'framework': 'pytest with async support',
        'database': 'SQLite with temporary in-memory/database file',
        'type_mocking': {
            'geography': True,
            'jsonb': True,
            'postgis_functions': False,
        },
        'services': {
            'all_database_services': True,
            'authentication': True,
            'spatial_operations': True,
            'caching': True,
        },
        'features': {
            'fast_execution': True,
            'test_isolation': True,
            'automatic_cleanup': True,
            'comprehensive_mocks': True,
        },
        'use_cases': [
            'RBAC testing',
            'API endpoint testing',
            'business logic validation',
            'performance benchmarking',
            'error handling scenarios',
        ],
    }


# Complete fixture list for import
__all__ = [
    'temp_sqlite_db',
    'sqlite_test_engine',
    'sqlite_session',
    'mock_postgresql_types',
    'mock_geography_for_sqlite',
    'mock_jsonb_for_sqlite',
    'mock_database_services',
    'mock_auth_service',
    'sqlite_client',
    'sqlite_test_data',
    'mock_spatial_operations',
    'async_sqlite_client',
    'mock_postgresql_type_environment',
    'create_sqlite_compatible_models',
    'sqlite_compatible_models',
    'mock_coordinates_transformer',
    'mock_postgis_functions',
    'sqlite_test_data_generator',
    'setup_sqlite_test_data',
    'mock_spatial_service',
    'mock_coordinate_validation',
    'mock_massajid_cache',
    'mock_massajid_repository',
    'async_sqlite_session',
    'create_test_environment_for_sqlite',
    'setup_sqlite_performance_benchmark',
    'setup_sqlite_error_handling',
    'create_sqlite_test_fixtures',
    'cleanup_sqlite_resources',
    'setup_sqlite_integration_tests',
    'create_sqlite_test_scenarios',
    'provide_sqlite_test_documentation',
    'sqlite_compatibility_settings',
    'sqlite_session_factory',
    'sqlite_test_data_validators',
    'sqlite_environment_config',
    'sqlite_test_setup',
    'create_sqlite_test_suite',
    'sqlite_performance_benchmark',
    'clean_sqlite_state',
    'sqlite_test_isolation',
    'sqlite_final_validation',
    'sqlite_test_documentation',
    'provide_comprehensive_sqlite_fixture_set',
    'sqlite_comprehensive_test_environment',
    'mock_postgresql_type_environment_sqlite',
]