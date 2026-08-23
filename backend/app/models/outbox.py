"""Domain events and outbox pattern for audit trails.

This module implements the outbox pattern for audit events, ensuring that
business changes and audit events are written in the same transaction.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.enums import enum_values

logger = logging.getLogger(__name__)


class OutboxEvent(Base):
    """Outbox event for domain events."""

    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, index=True
    )
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )
    published: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    last_error: Mapped[str | None] = mapped_column(Text)
    masjid_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("masjids.id"), index=True
    )

    # Relationships
    masjid: Mapped["Masjid"] = relationship(back_populates="outbox_events")