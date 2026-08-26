"""RBAC API tests for people endpoint - all roles."""

import pytest

from .conftest import SAMPLE_PERSON_DATA, SUPER_ADMIN_HEADERS, TEST_MASJID_ID, VIEWER_HEADERS, make_masjid_editor_headers, make_salat_editor_headers


@pytest.mark.asyncio
class TestPeopleSuperAdmin:
    """Super Admin can CRUD all people."""

    async def test_list_people(self, client):
        response = await client.get("/api/v1/people/", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_create_person(self, client):
        response = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 201

    async def test_update_person(self, client):
        create_resp = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=SUPER_ADMIN_HEADERS)
        person_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/people/{person_id}", json={"full_name": "Updated"}, headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_delete_person(self, client):
        create_resp = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=SUPER_ADMIN_HEADERS)
        person_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/people/{person_id}", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestPeopleMasjidEditor:
    """Masjid Editor: CRU own, no DELETE."""

    async def test_list_people(self, client):
        response = await client.get("/api/v1/people/", headers=make_masjid_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create_for_other_masjid(self, client):
        data = SAMPLE_PERSON_DATA.copy()
        data["masjid_id"] = "other-masjid"
        response = await client.post("/api/v1/people/", json=data, headers=make_masjid_editor_headers("different"))
        assert response.status_code == 403

    async def test_update_own(self, client):
        create_resp = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=SUPER_ADMIN_HEADERS)
        person_id = create_resp.json()["id"]
        response = await client.patch(f"/api/v1/people/{person_id}", json={"full_name": "Updated"}, headers=make_masjid_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 200

    async def test_cannot_delete(self, client):
        create_resp = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=SUPER_ADMIN_HEADERS)
        person_id = create_resp.json()["id"]
        response = await client.delete(f"/api/v1/people/{person_id}", headers=make_masjid_editor_headers(TEST_MASJID_ID))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestPeopleSalatEditor:
    """Salat Editor: R all, no CRUD."""

    async def test_list_people(self, client):
        response = await client.get("/api/v1/people/", headers=make_salat_editor_headers("any"))
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=make_salat_editor_headers("any"))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestPeopleViewer:
    """Viewer: R all, no CRUD."""

    async def test_list_people(self, client):
        response = await client.get("/api/v1/people/", headers=VIEWER_HEADERS)
        assert response.status_code == 200

    async def test_cannot_create(self, client):
        response = await client.post("/api/v1/people/", json=SAMPLE_PERSON_DATA, headers=VIEWER_HEADERS)
        assert response.status_code == 403