"""RBAC API tests for photos endpoint - all roles."""

import pytest

from .conftest import SAMPLE_PHOTO_DATA, SUPER_ADMIN_HEADERS, TEST_MASJID_ID, VIEWER_HEADERS, make_masjid_editor_headers, make_salat_editor_headers


@pytest.mark.asyncio
class TestPhotosSuperAdmin:
    """Super Admin: C/D all photos."""

    async def test_create_photo_own_masjid(self, client):
        response = await client.post(
            f"/api/v1/photos/masjids/{TEST_MASJID_ID}/photos",
            json=SAMPLE_PHOTO_DATA,
            headers=SUPER_ADMIN_HEADERS
        )
        assert response.status_code in [201, 404, 500]

    async def test_delete_photo_any_masjid(self, client):
        response = await client.delete(
            f"/api/v1/photos/masjids/{TEST_MASJID_ID}/photos/00000000-0000-0000-0000-000000000999",
            headers=SUPER_ADMIN_HEADERS
        )
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestPhotosMasjidEditor:
    """Masjid Editor: C/D own, C/D other blocked."""

    async def test_create_photo_own_masjid(self, client):
        response = await client.post(
            f"/api/v1/photos/masjids/{TEST_MASJID_ID}/photos",
            json=SAMPLE_PHOTO_DATA,
            headers=make_masjid_editor_headers(TEST_MASJID_ID)
        )
        assert response.status_code in [201, 404, 500]

    async def test_cannot_create_for_other_masjid(self, client):
        response = await client.post(
            "/api/v1/photos/masjids/00000000-0000-0000-0000-000000000002/photos",
            json=SAMPLE_PHOTO_DATA,
            headers=make_masjid_editor_headers("different-masjid")
        )
        assert response.status_code == 403

    async def test_cannot_delete_other_masjid(self, client):
        response = await client.delete(
            "/api/v1/photos/masjids/00000000-0000-0000-0000-000000000002/photos/00000000-0000-0000-0000-000000000999",
            headers=make_masjid_editor_headers("different-masjid")
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestPhotosSalatEditor:
    """Salat Editor: no photo access."""

    async def test_cannot_create_photo(self, client):
        response = await client.post(
            f"/api/v1/photos/masjids/{TEST_MASJID_ID}/photos",
            json=SAMPLE_PHOTO_DATA,
            headers=make_salat_editor_headers("any")
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestPhotosViewer:
    """Viewer: no photo access."""

    async def test_cannot_create_photo(self, client):
        response = await client.post(
            f"/api/v1/photos/masjids/{TEST_MASJID_ID}/photos",
            json=SAMPLE_PHOTO_DATA,
            headers=VIEWER_HEADERS
        )
        assert response.status_code == 403