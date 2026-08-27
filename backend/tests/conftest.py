"""Shared pytest fixtures for backend API tests.

Note: This uses mocking because the actual database models use PostgreSQL-specific
types (Geography, JSONB) that aren't supported by SQLite. The auth service
is mocked to allow testing RBAC behavior without database dependency.
"""

import pytest
import pytest_asyncio
import uuid
from typing import AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.auth import User
from app.db import get_db
from app.config import settings


# Token headers for different roles
SUPER_ADMIN_HEADERS = {"X-Super-Admin-Token": "dev-super-admin-token"}

# For Masjid Editor, we use a fake masjid UUID
TEST_MASJID_ID = "00000000-0000-0000-0000-000000000001"

def make_masjid_editor_headers(masjid_id: str = TEST_MASJID_ID) -> Dict[str, str]:
    """Create headers for Masjid Editor role with specific masjid_id."""
    return {"X-Masjid-Editor-Token": masjid_id}


def make_salat_editor_headers(masjid_id: str = TEST_MASJID_ID) -> Dict[str, str]:
    """Create headers for Salat Editor role with specific masjid_id."""
    return {
        "X-Salat-Editor-Token": masjid_id,
        "X-Dev-User-Masjid-Id": masjid_id
    }


VIEWER_HEADERS = {"X-Viewer-Token": "viewer-token"}


# Test data helpers matching the API schemas
SAMPLE_MASJID_DATA = {
    "name": "Test Masjid",
    "address_line1": "123 Test Street",
    "city": "Test City",
    "state": "Test State",
    "country": "IN",
    "latitude": 30.3165,
    "longitude": 78.0322,
    "timezone": "Asia/Kolkata",
}

SAMPLE_SALAT_DATA = {
    "masjid_id": TEST_MASJID_ID,
    "salat_name": "fajr",
    "adhan_time": "05:00:00",
    "iqama_time": "05:30:00",
}

SAMPLE_PROGRAM_DATA = {
    "masjid_id": TEST_MASJID_ID,
    "type": "maktab",
    "name": "Test Program",
    "description": "Test description",
    "max_participants": 50,
    "is_active": True,
}

SAMPLE_PERSON_DATA = {
    "masjid_id": TEST_MASJID_ID,
    "full_name": "Test Person",
    "role": "imam",
    "access_level": "viewer",
    "phone_primary": "+919876543210",
    "email": "test@example.com",
    "is_active": True,
}

SAMPLE_PHOTO_DATA = {
    "filename": "test.jpg",
    "file_path": "/uploads/test.jpg",
    "mime_type": "image/jpeg",
    "size": 1024,
    "caption": "Test photo",
    "order_index": 0,
    "is_featured": False,
}


@pytest_asyncio.fixture
async def mock_db() -> AsyncMock:
    """Provide a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def client(mock_db: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with mock database and mocked services."""
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Mock the services to avoid actual database calls
    # Patch where the services are DEFINED (app.services), since routers access them via app.services.*
    with patch("app.services.get_masjid_service") as mock_masjid_svc, \
         patch("app.services.get_salat_service") as mock_salat_svc, \
         patch("app.services.get_program_service") as mock_program_svc, \
         patch("app.services.get_person_service") as mock_person_svc, \
         patch("app.services.get_photo_service") as mock_photo_svc, \
         patch("app.services.get_sync_service") as mock_sync_svc:
        
# Make the mocks return AsyncMock service instances with sensible return values
        mock_masjid_instance = AsyncMock()
        mock_masjid_instance.get_by_id.return_value = None
        mock_masjid_instance.list_masjids.return_value = []
        # Return an object with all attributes the router response expects
        created_masjid = AsyncMock()
        created_masjid.id = TEST_MASJID_ID
        created_masjid.name = SAMPLE_MASJID_DATA["name"]
        created_masjid.address_line1 = SAMPLE_MASJID_DATA["address_line1"]
        created_masjid.address_line2 = None
        created_masjid.city = SAMPLE_MASJID_DATA["city"]
        created_masjid.state = SAMPLE_MASJID_DATA["state"]
        created_masjid.postal_code = None
        created_masjid.country = SAMPLE_MASJID_DATA["country"]
        created_masjid.latitude = SAMPLE_MASJID_DATA["latitude"]
        created_masjid.longitude = SAMPLE_MASJID_DATA["longitude"]
        created_masjid.timezone = SAMPLE_MASJID_DATA["timezone"]
        created_masjid.created_at = None
        created_masjid.updated_at = None
        mock_masjid_instance.create_masjid.return_value = created_masjid
        mock_masjid_instance.update_masjid.return_value = created_masjid
        mock_masjid_instance.delete_masjid.return_value = True
        mock_masjid_svc.return_value = mock_masjid_instance

        mock_salat_instance = AsyncMock()
        mock_salat_instance.get_by_id.return_value = None
        mock_salat_instance.list_schedules.return_value = []
        mock_salat_instance.create_schedule.return_value = {"id": str(uuid.uuid4()), **SAMPLE_SALAT_DATA}
        mock_salat_instance.update_schedule.return_value = {"id": str(uuid.uuid4()), **SAMPLE_SALAT_DATA}
        mock_salat_instance.delete_schedule.return_value = True
        mock_salat_svc.return_value = mock_salat_instance

        mock_program_instance = AsyncMock()
        mock_program_instance.get_by_id.return_value = None
        mock_program_instance.list_programs.return_value = []
        mock_program_instance.create_program.return_value = {"id": str(uuid.uuid4()), **SAMPLE_PROGRAM_DATA}
        mock_program_instance.update_program.return_value = {"id": str(uuid.uuid4()), **SAMPLE_PROGRAM_DATA}
        mock_program_instance.delete_program.return_value = True
        mock_program_svc.return_value = mock_program_instance

        mock_person_instance = AsyncMock()
        mock_person_instance.get_by_id.return_value = None
        mock_person_instance.list_people.return_value = []
        mock_person_instance.create_person.return_value = {"id": str(uuid.uuid4()), **SAMPLE_PERSON_DATA}
        mock_person_instance.update_person.return_value = {"id": str(uuid.uuid4()), **SAMPLE_PERSON_DATA}
        mock_person_instance.delete_person.return_value = True
        mock_person_svc.return_value = mock_person_instance

        mock_photo_instance = AsyncMock()
        mock_photo_instance.create_photo.return_value = {"id": str(uuid.uuid4()), **SAMPLE_PHOTO_DATA}
        mock_photo_instance.delete_photo.return_value = True
        mock_photo_svc.return_value = mock_photo_instance

        mock_sync_instance = AsyncMock()
        mock_sync_instance.get_snapshot.return_value = {
            "snapshot": {"masjids": [], "salat_schedules": [], "programs": [], "people": [], "photos": []},
            "cursor": "1234567890.0",
            "has_more": False
        }
        mock_sync_instance.process_mutations.return_value = []
        mock_sync_svc.return_value = mock_sync_instance
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    
    app.dependency_overrides.clear()