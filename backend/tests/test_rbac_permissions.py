"""RBAC Permission Tests - Unit tests for auth service permissions.

These tests validate the RBAC matrix without requiring a database connection.
"""

import pytest
import uuid
from app.auth import AuthService, User


auth_service = AuthService()


def make_user(role: str, masjid_id: str = None) -> User:
    """Helper to create a user with specific role and masjid_id."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"{role}@test.com",
        access_level="admin",
        role=role,
        name=role.replace("_", " ").title(),
        masjid_id=masjid_id,
    )
    user.permissions = auth_service._get_permissions_for_role(role)
    return user


@pytest.mark.asyncio
class TestSuperAdminPermissions:
    """Super Admin has full access to everything."""
    
    @pytest.fixture
    def user(self):
        return make_user("super_admin")
    
    def test_masjid_crud_all(self, user):
        assert user.has_permission("masjid:read")
        assert user.has_permission("masjid:create")
        assert user.has_permission("masjid:update")
        assert user.has_permission("masjid:delete")
    
    def test_salat_crud_all(self, user):
        assert user.has_permission("salat:read")
        assert user.has_permission("salat:create")
        assert user.has_permission("salat:update")
        assert user.has_permission("salat:delete")
    
    def test_program_crud_all(self, user):
        assert user.has_permission("program:read")
        assert user.has_permission("program:create")
        assert user.has_permission("program:update")
        assert user.has_permission("program:delete")
    
    def test_person_crud_all(self, user):
        assert user.has_permission("person:read")
        assert user.has_permission("person:create")
        assert user.has_permission("person:update")
        assert user.has_permission("person:delete")
    
    def test_photo_crud_all(self, user):
        assert user.has_permission("photo:read")
        assert user.has_permission("photo:create")
        assert user.has_permission("photo:delete")
    
    def test_sync_rw_all(self, user):
        assert user.has_permission("sync:read")
        assert user.has_permission("sync:write")
    
    def test_admin_rw_all(self, user):
        assert user.has_permission("admin:read")
        assert user.has_permission("admin:approve")
    
    def test_audit_read_all(self, user):
        assert user.has_permission("audit:read")


@pytest.mark.asyncio
class TestMasjidEditorPermissions:
    """Masjid Editor has scoped access."""
    
    @pytest.fixture
    def user(self):
        return make_user("masjid_editor", masjid_id="test-masjid-001")
    
    def test_masjid_read_all(self, user):
        assert user.has_permission("masjid:read")
    
    def test_masjid_create(self, user):
        assert user.has_permission("masjid:create")
    
    def test_masjid_update_own(self, user):
        assert user.has_permission("masjid:update", "test-masjid-001")
        assert not user.has_permission("masjid:update", "other-masjid")
    
    def test_masjid_delete_never(self, user):
        assert not user.has_permission("masjid:delete")
    
    def test_salat_read_all(self, user):
        assert user.has_permission("salat:read")
    
    def test_salat_create_own(self, user):
        assert user.has_permission("salat:create", "test-masjid-001")
        assert not user.has_permission("salat:create", "other-masjid")
    
    def test_salat_update_own(self, user):
        assert user.has_permission("salat:update", "test-masjid-001")
        assert not user.has_permission("salat:update", "other-masjid")
    
    def test_salat_delete_never(self, user):
        assert not user.has_permission("salat:delete")
    
    def test_photo_crud_own(self, user):
        assert user.has_permission("photo:read")
        assert user.has_permission("photo:create", "test-masjid-001")
        assert user.has_permission("photo:delete", "test-masjid-001")
    
    def test_admin_read_approve_own(self, user):
        assert user.has_permission("admin:read")
        assert user.has_permission("admin:approve", "test-masjid-001")


@pytest.mark.asyncio
class TestSalatEditorPermissions:
    """Salat Editor inherits viewer for most, RU salat."""
    
    @pytest.fixture
    def user(self):
        return make_user("salat_editor", masjid_id="test-masjid-001")
    
    def test_masjid_read_only(self, user):
        assert user.has_permission("masjid:read")
        assert not user.has_permission("masjid:create")
        assert not user.has_permission("masjid:update")
        assert not user.has_permission("masjid:delete")
    
    def test_salat_read_all(self, user):
        assert user.has_permission("salat:read")
    
    def test_salat_create_never(self, user):
        assert not user.has_permission("salat:create")
    
    def test_salat_update_own(self, user):
        assert user.has_permission("salat:update", "test-masjid-001")
        assert not user.has_permission("salat:update", "other-masjid")
    
    def test_salat_delete_never(self, user):
        assert not user.has_permission("salat:delete")
    
    def test_inherits_viewer_for_others(self, user):
        assert user.has_permission("program:read")
        assert user.has_permission("person:read")
        assert not user.has_permission("photo:create")


@pytest.mark.asyncio
class TestViewerPermissions:
    """Viewer has read-only access."""
    
    @pytest.fixture
    def user(self):
        return make_user("viewer")
    
    def test_read_all_masjids(self, user):
        assert user.has_permission("masjid:read")
    
    def test_create_never(self, user):
        assert not user.has_permission("masjid:create")
        assert not user.has_permission("salat:create")
        assert not user.has_permission("program:create")
        assert not user.has_permission("person:create")
    
    def test_update_never(self, user):
        assert not user.has_permission("masjid:update")
        assert not user.has_permission("salat:update")
        assert not user.has_permission("program:update")
        assert not user.has_permission("person:update")
    
    def test_delete_never(self, user):
        assert not user.has_permission("masjid:delete")
        assert not user.has_permission("salat:delete")
        assert not user.has_permission("program:delete")
        assert not user.has_permission("person:delete")
    
    def test_no_secret_access(self, user):
        assert not user.has_permission("sync:read")
        assert not user.has_permission("sync:write")
        assert not user.has_permission("admin:read")
        assert not user.has_permission("admin:approve")
        assert not user.has_permission("audit:read")
        assert not user.has_permission("photo:create")
        assert not user.has_permission("photo:delete")