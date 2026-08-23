"""Authentication and authorization service for the Jumapp API.

This module implements the authentication layer using dev mode for development.
In production, this would be replaced with a proper identity provider integration.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings


from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

# Security schemes for OpenAPI documentation
security_bearer = HTTPBearer(auto_error=False)
security_super_admin = APIKeyHeader(name="X-Super-Admin-Token", auto_error=False)
security_masjid_editor = APIKeyHeader(name="X-Masjid-Editor-Token", auto_error=False)
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
        if masjid_id and self.masjid_id != masjid_id:
            return False
        return self.permissions.get(permission, False)

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

        # 3. Check detailed dev user headers
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
        base_permissions = {
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

        if role in ["super_admin", "masjid_editor", "salat_editor"]:
            base_permissions.update({
                "masjid:read": True,
                "masjid:create": role == "masjid_editor",
                "masjid:update": role == "masjid_editor",
                "masjid:delete": role == "masjid_editor",
                "salat:read": True,
                "salat:create": role in ["masjid_editor", "salat_editor"],
                "salat:update": role in ["masjid_editor", "salat_editor"],
                "salat:delete": role == "masjid_editor",
            })

        if role == "super_admin":
            base_permissions.update({
                "admin:read": True,
                "admin:approve": True,
            })

        return base_permissions

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
