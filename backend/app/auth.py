"""Authentication and authorization service for the Jumapp API.

This module implements the authentication layer using dev mode for development.
In production, this would be replaced with a proper identity provider integration.
"""

import uuid
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings


from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

# Security schemes for OpenAPI documentation
security_bearer = HTTPBearer(auto_error=False)
security_super_admin = APIKeyHeader(name="X-Super-Admin-Token", auto_error=False)
security_masjid_editor = APIKeyHeader(name="X-Masjid-Editor-Token", auto_error=False)
security_salat_editor = APIKeyHeader(name="X-Salat-Editor-Token", auto_error=False)
security_viewer = APIKeyHeader(name="X-Viewer-Token", auto_error=False)
security_dev_user = APIKeyHeader(name="X-Dev-User-Token", auto_error=False)


class User:
    """User model for authenticated requests."""

    def __init__(
        self,
        id: str,
        email: str,
        access_level: str,
        role: str,
        name: str,
        masjid_id: Optional[str] = None,
    ):
        self.id = id
        self.email = email
        self.access_level = access_level
        self.role = role
        self.name = name
        self.masjid_id = masjid_id
        self.permissions: Dict[str, bool] = {}

    def has_permission(self, permission: str, masjid_id: Optional[str] = None) -> bool:
        """Check if the user has a specific permission."""
        # 1. Super Admin bypasses masjid_id restrictions for granted permissions
        if self.role == "super_admin":
            return self.permissions.get(permission, False)

        # 2. Check basic permission flag
        if not self.permissions.get(permission, False):
            return False

        # 3. Read permissions are globally accessible across masjids if the user has read permission
        if permission.endswith(":read"):
            return True

        # 4. Scoped write/update/delete check if a specific masjid_id is specified
        if masjid_id and self.masjid_id:
            return str(self.masjid_id) == str(masjid_id)

        return True

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class AuthService:
    """Authentication service for managing user sessions and tokens."""

    def __init__(self):
        self.super_admin_token = settings.super_admin_token
        self.super_admin_email = "superadmin@jumapp.com"
        self.super_admin_user_id = str(uuid.uuid4())

    def get_dev_user_from_request(self, request: Request) -> Optional[User]:
        """Get dev user from request headers for dev mode."""
        # 1. Check Super Admin Token
        token = request.headers.get("X-Super-Admin-Token") or request.headers.get("X-Dev-User-Token")
        if token and token == self.super_admin_token:
            user = User(
                id=self.super_admin_user_id,
                email=self.super_admin_email,
                access_level="admin",
                role="super_admin",
                name="Super Admin",
            )
            user.permissions = self._get_permissions_for_role("super_admin")
            return user

        # 2. Check Masjid Editor Token
        editor_masjid_id = request.headers.get("X-Masjid-Editor-Token")
        if editor_masjid_id:
            user = User(
                id=str(uuid.uuid4()),
                email=f"editor-{editor_masjid_id[:8]}@jumapp.com",
                access_level="editor",
                role="masjid_editor",
                name="Masjid Editor",
                masjid_id=editor_masjid_id,
            )
            user.permissions = self._get_permissions_for_role("masjid_editor")
            return user

        # 3. Check Salat Editor Token
        salat_editor_token = request.headers.get("X-Salat-Editor-Token")
        if salat_editor_token:
            user = User(
                id=str(uuid.uuid4()),
                email="salat-editor@jumapp.com",
                access_level="editor",
                role="salat_editor",
                name="Salat Editor",
                masjid_id=request.headers.get("X-Dev-User-Masjid-Id"),
            )
            user.permissions = self._get_permissions_for_role("salat_editor")
            return user

        # 4. Check Viewer Token
        viewer_token = request.headers.get("X-Viewer-Token")
        if viewer_token:
            user = User(
                id=str(uuid.uuid4()),
                email="viewer@jumapp.com",
                access_level="viewer",
                role="viewer",
                name="Viewer",
            )
            user.permissions = self._get_permissions_for_role("viewer")
            return user

        # 5. Check detailed dev user headers
        user_id = request.headers.get("X-Dev-User-Id")
        email = request.headers.get("X-Dev-User-Email")
        role = request.headers.get("X-Dev-User-Role")
        access_level = request.headers.get("X-Dev-User-Access-Level")
        name = request.headers.get("X-Dev-User-Name")
        masjid_id = request.headers.get("X-Dev-User-Masjid-Id")

        if all([user_id, email, role, access_level, name]):
            user = User(
                id=user_id,
                email=email,
                access_level=access_level,
                role=role,
                name=name,
                masjid_id=masjid_id,
            )
            user.permissions = self._get_permissions_for_role(role)
            return user

        return None

    def _get_permissions_for_role(self, role: str) -> Dict[str, bool]:
        """Get permissions for a specific role."""
        if role == "super_admin":
            return {
                "masjid:read": True,
                "masjid:create": True,
                "masjid:update": True,
                "masjid:delete": True,
                "salat:read": True,
                "salat:create": True,
                "salat:update": True,
                "salat:delete": True,
                "program:read": True,
                "program:create": True,
                "program:update": True,
                "program:delete": True,
                "person:read": True,
                "person:create": True,
                "person:update": True,
                "person:delete": True,
                "photo:read": True,
                "photo:create": True,
                "photo:delete": True,
                "sync:read": True,
                "sync:write": True,
                "admin:read": True,
                "admin:approve": True,
            }

        if role == "masjid_editor":
            return {
                "masjid:read": True,
                "masjid:create": True,
                "masjid:update": True,
                "masjid:delete": True,
                "salat:read": True,
                "salat:create": True,
                "salat:update": True,
                "salat:delete": True,
                "program:read": True,
                "program:create": True,
                "program:update": True,
                "program:delete": True,
                "person:read": True,
                "person:create": True,
                "person:update": True,
                "person:delete": True,
                "photo:read": True,
                "photo:create": True,
                "photo:delete": True,
                "sync:read": True,
                "sync:write": True,
                "admin:read": False,
                "admin:approve": False,
            }

        if role == "salat_editor":
            return {
                "masjid:read": True,
                "masjid:create": False,
                "masjid:update": False,
                "masjid:delete": False,
                "salat:read": True,
                "salat:create": False,
                "salat:update": True,
                "salat:delete": False,
                "program:read": True,
                "program:create": False,
                "program:update": False,
                "program:delete": False,
                "person:read": True,
                "person:create": False,
                "person:update": False,
                "person:delete": False,
                "photo:read": True,
                "photo:create": False,
                "photo:delete": False,
                "sync:read": True,
                "sync:write": False,
                "admin:read": False,
                "admin:approve": False,
            }

        # Default role: Viewer
        return {
            "masjid:read": True,
            "masjid:create": False,
            "masjid:update": False,
            "masjid:delete": False,
            "salat:read": True,
            "salat:create": False,
            "salat:update": False,
            "salat:delete": False,
            "program:read": True,
            "program:create": False,
            "program:update": False,
            "program:delete": False,
            "person:read": True,
            "person:create": False,
            "person:update": False,
            "person:delete": False,
            "photo:read": True,
            "photo:create": False,
            "photo:delete": False,
            "sync:read": True,
            "sync:write": False,
            "admin:read": False,
            "admin:approve": False,
        }

    async def get_current_user(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = None,
    ) -> User:
        """Get the current authenticated user from the request."""
        if settings.auth_mode == "dev":
            user = self.get_dev_user_from_request(request)
            if user:
                return user
            # Default dev user when in dev mode
            dev_user = User(
                id=self.super_admin_user_id,
                email=self.super_admin_email,
                access_level="admin",
                role="super_admin",
                name="Super Admin",
            )
            dev_user.permissions = self._get_permissions_for_role("super_admin")
            return dev_user

        if credentials and credentials.credentials:
            user = self.get_dev_user_from_request(request)
            if user:
                return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication credentials",
        )

    def require_auth(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = None,
    ) -> User:
        """Dependency to require authentication."""
        user = self.get_dev_user_from_request(request)
        if user:
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )


# Global auth service instance
_auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Get the auth service instance."""
    return _auth_service


security_optional = HTTPBearer(auto_error=False)


async def get_current_user_dependency(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
) -> User:
    """FastAPI dependency for getting the current user."""
    return await _auth_service.get_current_user(request, credentials)
