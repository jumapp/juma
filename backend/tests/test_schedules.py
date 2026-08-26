"""RBAC API tests for schedules endpoint - all roles."""

import pytest

from .conftest import SAMPLE_SALAT_DATA, SUPER_ADMIN_HEADERS, TEST_MASJID_ID, VIEWER_HEADERS, make_masjid_editor_headers, make_salat_editor_headers


@pytest.mark.asyncio
class TestSchedulesSuperAdmin:
    """Super Admin can CRUD all schedules."""

    async def test_list_schedules(self, client):
        response = await client.get("/api/v1/schedules/", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_create_schedule(self, client):
        response = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 201

    async def test_update_schedule(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/schedules/{schedule_id}", json={"adhan_time": "05:30:00"}, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_delete_schedule(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/schedules/{schedule_id}", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestSchedulesMasjidEditor:
    """Masjid Editor: R all, CRU own, no DELETE."""

    async def test_list_schedules(self, client):
        response = await client.get("/api/v1/schedules/", headers=make_masjid_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create_for_other_masjid(self, client):
        data = SAMPLE_SALAT_DATA.copy()
        data["masjid_id"] = "other-masjid"
        response = await client.post("/api/v1/schedules/", json=data, headers=make_masjid_editor_headers("different"))
        assert response.status_code == 403

    async def test_update_own(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/schedules/{schedule_id}", json={"adhan_time": "05:30:00"}, headers=make_masjid_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 200

    async def test_cannot_delete(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/schedules/{schedule_id}", headers=make_masjid_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestSchedulesSalatEditor:
    """Salat Editor: R all, RU own."""

    async def test_list_schedules(self, client):
        response = await client.get("/api/v1/schedules/", headers=make_salat_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=make_salat_editor_headers("any"))
        assert response.status_code == 403

    async def test_update_own(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/schedules/{schedule_id}", json={"adhan_time": "05:30:00"}, headers=make_salat_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 200

    async def test_cannot_delete(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/schedules/{schedule_id}", headers=make_salat_editor_headers("any"))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestSchedulesViewer:
    """Viewer: R all, no CRUD."""

    async def test_list_schedules(self, client):
        response = await client.get("/api/v1/schedules/", headers=VIEWER_HEADERS)
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=VIEWER_HEADERS)
        assert response.status_code == 403

    async def test_cannot_update(self, client):
        create_resp = await client.post("/api/v1/schedules/", json=SAMPLE_SALAT_DATA, headers=SUPER_ADMIN_HEADERS)
        schedule_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/schedules/{schedule_id}", json={"adhan_time": "05:30:00"}, headers=VIEWER_HEADERS)
        assert response.status_code == 403