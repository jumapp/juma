"""RBAC API tests for admin endpoints - all roles."""

import pytest

from .conftest import SUPER_ADMIN_HEADERS, TEST_MASJID_ID, VIEWER_HEADERS, make_masjid_editor_headers, make_salat_editor_headers


@pytest.mark.asyncio
class TestRoleRequestsSuperAdmin:
    """Super Admin: R all role requests, approve all."""

    async def test_list_role_requests(self, client):
        response = await client.get("/api/v1/admin/role-requests", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200

    async def test_approve_role_request(self, client):
        response = await client.patch(
            "/api/v1/admin/role-requests/00000000-0000-0000-0000-000000000999",
            json={"status": "approved"},
            headers=SUPER_ADMIN_HEADERS
        )
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestRoleRequestsMasjidEditor:
    """Masjid Editor: R/Approve own masjid_id only."""

    async def test_list_own_masjid_role_requests(self, client):
        response = await client.get(
            "/api/v1/admin/role-requests",
            headers=make_masjid_editor_headers(TEST_MASJID_ID)
        )
        assert response.status_code == 200

    async def test_cannot_approve_for_other_masjid(self, client):
        response = await client.patch(
            "/api/v1/admin/role-requests/00000000-0000-0000-0000-000000000999",
            json={"status": "approved"},
            headers=make_masjid_editor_headers("other-masjid-999")
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestRoleRequestsSalatEditor:
    """Salat Editor: no admin access."""

    async def test_cannot_list_role_requests(self, client):
        response = await client.get("/api/v1/admin/role-requests", headers=make_salat_editor_headers("any"))
        assert response.status_code == 403

    async def test_cannot_approve_role_request(self, client):
        response = await client.patch(
            "/api/v1/admin/role-requests/00000000-0000-0000-0000-000000000999",
            json={"status": "approved"},
            headers=make_salat_editor_headers("any")
        )
        assert response.status_code == 403


@pytest.mark.asyncio
class TestRoleRequestsViewer:
    """Viewer: no admin access."""

    async def test_cannot_list_role_requests(self, client):
        response = await client.get("/api/v1/admin/role-requests", headers=VIEWER_HEADERS)
        assert response.status_code == 403


@pytest.mark.asyncio
class TestAuditEventsSuperAdmin:
    """Super Admin: R all audit events."""

    async def test_list_audit_events(self, client):
        response = await client.get("/api/v1/admin/audit-events", headers=SUPER_ADMIN_HEADERS)
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAuditEventsMasjidEditor:
    """Masjid Editor: no audit events access."""

    async def test_cannot_list_audit_events(self, client):
        response = await client.get("/api/v1/admin/audit-events", headers=make_masjid_editor_headers("any"))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestAuditEventsSalatEditor:
    """Salat Editor: no audit events access."""

    async def test_cannot_list_audit_events(self, client):
        response = await client.get("/api/v1/admin/audit-events", headers=make_salat_editor_headers("any"))
        assert response.status_code == 403


@pytest.mark.asyncio
class TestAuditEventsViewer:
    """Viewer: no audit events access."""

    async def test_cannot_list_audit_events(self, client):
        response = await client.get("/api/v1/admin/audit-events", headers=VIEWER_HEADERS)
        assert response.status_code == 403