"""Domain events and outbox pattern for audit trails.

This module implements the outbox pattern for audit events, ensuring that
business changes and audit events are written in the same transaction.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from sqlalchemy import CheckConstraint, JSON, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin
from app.enums import enum_values


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    UPLOAD_PHOTO = "upload_photo"
    DELETE_PHOTO = "delete_photo"
    ASSIGN_ROLE = "assign_role"
    CHANGE_SCHEDULE = "change_schedule"


class AuditEvent(TimestampMixin, Base):
    """Audit event - immutable, append-only record of all business changes."""

    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint(
            "action IN ('create', 'update', 'delete', 'approve', 'reject', 'upload_photo', 'delete_photo', 'assign_role', 'change_schedule')",
            name="valid_audit_action"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    actor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, index=True
    )
    actor_type: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    before_state: Mapped[Dict[str, Any] | None] = mapped_column(JSON)
    after_state: Mapped[Dict[str, Any] | None] = mapped_column(JSON)
    reason: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[str | None] = mapped_column(Text, index=True)
    session_id: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(Text)
    user_agent: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[Dict[str, Any] | None] = mapped_column(
        JSON, server_default=text("'{}'::jsonb")
    )

    # Relationships
    # Note: No backref to avoid circular imports

    @classmethod
    def from_change(
        cls,
        actor_id: uuid.UUID,
        actor_type: str,
        action: AuditAction,
        entity_type: str,
        entity_id: uuid.UUID,
        before_state: Dict[str, Any] | None = None,
        after_state: Dict[str, Any] | None = None,
        reason: str | None = None,
        request_id: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        meta: Dict[str, Any] | None = None,
    ) -> "AuditEvent":
        """Create an audit event from a business change."""
        return cls(
            id=uuid.uuid4(),
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            reason=reason,
            request_id=request_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            meta=meta or {},
        )
