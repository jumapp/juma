"""RBAC API tests for masjids endpoint - all roles."""

import pytest

from .conftest import SAMPLE_MASJID_DATA, SUPER_ADMIN_HEADERS, VIEWER_HEADERS, make_masjid_editor_headers, make_salat_editor_headers


@pytest.mark.asyncio
class TestMasjidsSuperAdmin:
    """Super Admin can CRUD all masjids."""

    async def test_list_masjids(self, client):
        response = await client.get("/api/v1/masjids/", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_create_masjid(self, client):
        response = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 201
        assert response.json()["name"] == SAMPLE_MASJID_DATA["name"]

    async def test_update_masjid(self, client):
        create_resp = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=SUPER_ADMIN_HEADERS)
        assert create_resp.status_code == 201
        masjid_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/masjids/{masjid_id}", json={"name": "Updated"}, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_delete_masjid(self, client):
        create_resp = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=SUPER_ADMIN_HEADERS)
        assert create_resp.status_code == 201
        masjid_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/masjids/{masjid_id}", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestMasjidsMasjidEditor:
    """Masjid Editor: R all, CRU own, no DELETE."""

    async def test_list_masjids(self, client):
        response = await client.get("/api/v1/masjids/", headers=make_masjid_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create_for_other_masjid(self, client):
        response = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=make_masjid_editor_headers("other"))
        assert response.status_code == 403

    async def test_update_own(self, client):
        create_resp = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=SUPER_ADMIN_HEADERS)
        masjid_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/masjids/{masjid_id}", json={"name": "Updated"}, headers=make_masjid_editor_headers(masjid_id))
        assert response.status_code == 200

    async def test_cannot_delete(self, client):
        create_resp = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=SUPER_ADMIN_HEADERS)
        masjid_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/masjids/{masjid_id}", headers=make_masjid_editor_headers(masjid_id))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestMasjidsSalatEditor:
    """Salat Editor: R all, no CRUD."""

    async def test_list_masjids(self, client):
        response = await client.get("/api/v1/masjids/", headers=make_salat_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=make_salat_editor_headers("any"))
        assert response.status_code == 403

    async def test_cannot_update(self, client):
        create_resp = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=SUPER_ADMIN_HEADERS)
        masjid_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/masjids/{masjid_id}", json={"name": "Hack"}, headers=make_salat_editor_headers("any"))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestMasjidsViewer:
    """Viewer: R all, no CRUD."""

    async def test_list_masjids(self, client):
        response = await client.get("/api/v1/masjids/", headers=VIEWER_HEADERS)
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/masjids/", json=SAMPLE_MASJID_DATA, headers=VIEWER_HEADERS)
        assert response.status_code == 403