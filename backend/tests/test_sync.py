"""Sync API and Service Tests.

Tests snapshot retrieval, mutation batch processing, idempotency tracking,
and RBAC permission enforcement.
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import (
    SUPER_ADMIN_HEADERS,
    VIEWER_HEADERS,
    make_masjid_editor_headers,
    make_salat_editor_headers,
    TEST_MASJID_ID,
)
from app.services import SyncService
from app.models.masjid import Masjid
from app.models.salat import SalatSchedule
from app.models.program import MasjidProgram
from app.models.person import MasjidPerson


@pytest.mark.asyncio
class TestSyncSuperAdmin:
    """Super Admin has full access to sync read and write."""

    async def test_get_sync_snapshot(self, client):
        response = await client.get("/api/v1/sync/", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_post_sync_mutations_empty(self, client):
        response = await client.post(
            "/api/v1/sync/mutations",
            json={"mutations": []},
            headers=SUPER_ADMIN_HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert "processed" in data
        assert "failed" in data
        assert "results" in data

    async def test_post_sync_mutations_batch(self, client):
        mut_id_1 = str(uuid.uuid4())
        mut_id_2 = str(uuid.uuid4())
        payload = {
            "mutations": [
                {
                    "id": mut_id_1,
                    "entity": "masjid",
                    "type": "CREATE",
                    "payload": {
                        "name": "Offline Masjid",
                        "city": "Dehradun",
                    },
                },
                {
                    "id": mut_id_2,
                    "entity": "salat_schedule",
                    "type": "CREATE",
                    "payload": {
                        "masjid_id": TEST_MASJID_ID,
                        "salat_name": "fajr",
                        "iqama_time": "05:30:00",
                    },
                },
            ]
        }
        response = await client.post(
            "/api/v1/sync/mutations",
            json=payload,
            headers=SUPER_ADMIN_HEADERS,
        )
        assert response.status_code == 200


@pytest.mark.asyncio
class TestSyncPermissions:
    """Non-admin roles cannot access sync endpoints."""

    async def test_masjid_editor_cannot_get_sync_snapshot(self, client):
        response = await client.get("/api/v1/sync/", headers=make_masjid_editor_headers("any"))
        assert response.status_code == 403

    async def test_masjid_editor_cannot_post_sync_mutations(self, client):
        response = await client.post(
            "/api/v1/sync/mutations",
            json={"mutations": []},
            headers=make_masjid_editor_headers("any"),
        )
        assert response.status_code == 403

    async def test_salat_editor_cannot_get_sync_snapshot(self, client):
        response = await client.get("/api/v1/sync/", headers=make_salat_editor_headers("any"))
        assert response.status_code == 403

    async def test_salat_editor_cannot_post_sync_mutations(self, client):
        response = await client.post(
            "/api/v1/sync/mutations",
            json={"mutations": []},
            headers=make_salat_editor_headers("any"),
        )
        assert response.status_code == 403

    async def test_viewer_cannot_get_sync_snapshot(self, client):
        response = await client.get("/api/v1/sync/", headers=VIEWER_HEADERS)
        assert response.status_code == 403

    async def test_viewer_cannot_post_sync_mutations(self, client):
        response = await client.post(
            "/api/v1/sync/mutations",
            json={"mutations": []},
            headers=VIEWER_HEADERS,
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestSyncServiceLogic:
    """Unit tests for SyncService mutation processing and idempotency."""

    @pytest.fixture
    def sync_service(self):
        session = AsyncMock()
        service = SyncService(session)
        service.masjid_repo = AsyncMock()
        service.salat_repo = AsyncMock()
        service.program_repo = AsyncMock()
        service.person_repo = AsyncMock()
        service.photo_repo = AsyncMock()
        # Reset processed mutation IDs for isolation
        SyncService._processed_mutation_ids = set()
        return service

    async def test_process_masjid_create(self, sync_service):
        mut_id = str(uuid.uuid4())
        mutation = {
            "id": mut_id,
            "entity": "masjid",
            "type": "CREATE",
            "payload": {"name": "Test Masjid", "city": "Dehradun"},
        }
        sync_service.masjid_repo.create.return_value = {"id": mut_id, "name": "Test Masjid"}
        
        results = await sync_service.process_mutations([mutation])
        assert len(results) == 1
        assert results[0]["id"] == mut_id
        assert results[0]["status"] == "processed"

    async def test_process_idempotency_duplicate(self, sync_service):
        mut_id = str(uuid.uuid4())
        mutation = {
            "id": mut_id,
            "entity": "masjid",
            "type": "CREATE",
            "payload": {"name": "Test Masjid", "city": "Dehradun"},
        }
        sync_service.masjid_repo.create.return_value = {"id": mut_id, "name": "Test Masjid"}
        
        # First attempt -> processed
        results1 = await sync_service.process_mutations([mutation])
        assert results1[0]["status"] == "processed"

        # Second attempt with same ID -> duplicate
        results2 = await sync_service.process_mutations([mutation])
        assert results2[0]["status"] == "duplicate"

    async def test_process_salat_create(self, sync_service):
        mut_id = str(uuid.uuid4())
        mutation = {
            "id": mut_id,
            "entity": "salat_schedule",
            "type": "CREATE",
            "payload": {"masjid_id": str(uuid.uuid4()), "salat_name": "fajr"},
        }
        sync_service.salat_repo.create.return_value = {"id": mut_id}
        results = await sync_service.process_mutations([mutation])
        assert results[0]["status"] == "processed"

    async def test_process_program_and_person(self, sync_service):
        p_id = str(uuid.uuid4())
        person_id = str(uuid.uuid4())
        mutations = [
            {
                "id": p_id,
                "entity": "program",
                "type": "CREATE",
                "payload": {"name": "Maktab", "masjid_id": str(uuid.uuid4())},
            },
            {
                "id": person_id,
                "entity": "person",
                "type": "CREATE",
                "payload": {"full_name": "Imam", "masjid_id": str(uuid.uuid4())},
            },
        ]
        sync_service.program_repo.create.return_value = {"id": p_id}
        sync_service.person_repo.create.return_value = {"id": person_id}
        results = await sync_service.process_mutations(mutations)
        assert len(results) == 2
        assert results[0]["status"] == "processed"
        assert results[1]["status"] == "processed"

    async def test_unknown_entity_fails_gracefully(self, sync_service):
        mut_id = str(uuid.uuid4())
        mutation = {
            "id": mut_id,
            "entity": "unknown_entity",
            "type": "CREATE",
            "payload": {},
        }
        results = await sync_service.process_mutations([mutation])
        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "Unknown entity" in results[0]["error"]
