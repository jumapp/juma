"""RBAC API tests for programs endpoint - all roles."""

import pytest

from .conftest import SAMPLE_PROGRAM_DATA, SUPER_ADMIN_HEADERS, TEST_MASJID_ID, VIEWER_HEADERS, make_masjid_editor_headers, make_salat_editor_headers


@pytest.mark.asyncio
class TestProgramsSuperAdmin:
    """Super Admin can CRUD all programs."""

    async def test_list_programs(self, client):
        response = await client.get("/api/v1/programs/", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_create_program(self, client):
        response = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 201

    async def test_update_program(self, client):
        create_resp = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=SUPER_ADMIN_HEADERS)
        program_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/programs/{program_id}", json={"name": "Updated"}, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_delete_program(self, client):
        create_resp = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=SUPER_ADMIN_HEADERS)
        program_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/programs/{program_id}", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestProgramsMasjidEditor:
    """Masjid Editor: CRUD own masjid_id."""

    async def test_list_programs(self, client):
        response = await client.get("/api/v1/programs/", headers=make_masjid_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create_for_other_masjid(self, client):
        data = SAMPLE_PROGRAM_DATA.copy()
        data["masjid_id"] = "other-masjid"
        response = await client.post("/api/v1/programs/", json=data, headers=make_masjid_editor_headers("different"))
        assert response.status_code == 403

    async def test_update_own(self, client):
        create_resp = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=SUPER_ADMIN_HEADERS)
        program_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/programs/{program_id}", json={"name": "Updated"}, headers=make_masjid_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 200

    async def test_delete_own(self, client):
        create_resp = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=SUPER_ADMIN_HEADERS)
        program_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/programs/{program_id}", headers=make_masjid_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 200


@pytest.mark.asyncio
class TestProgramsSalatEditor:
    """Salat Editor: R all, no CRUD."""

    async def test_list_programs(self, client):
        response = await client.get("/api/v1/programs/", headers=make_salat_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=make_salat_editor_headers("any"))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestProgramsViewer:
    """Viewer: R all, no CRUD."""

    async def test_list_programs(self, client):
        response = await client.get("/api/v1/programs/", headers=VIEWER_HEADERS)
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/programs/", json=SAMPLE_PROGRAM_DATA, headers=VIEWER_HEADERS)
        assert response.status_code == 403