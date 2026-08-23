"""Masjid aggregate root model."""

import uuid
from datetime import time
from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Masjid(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "masjids"
    __table_args__ = (
        CheckConstraint(
            "char_length(btrim(name)) BETWEEN 1 AND 200", name="name_length"
        ),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="latitude_range"),
        CheckConstraint(
            "longitude BETWEEN -180 AND 180", name="longitude_range"
        ),
        CheckConstraint("char_length(country) = 2", name="country_iso2"),
        CheckConstraint(
            "postal_code IS NULL OR postal_code ~ '^[0-9]{4,10}$'",
            name="postal_code_format",
        ),
        CheckConstraint(
            "is_24_hours OR (opens_at IS NOT NULL AND closes_at IS NOT NULL)",
            name="hours_required",
        ),
        CheckConstraint("is_24_hours OR opens_at < closes_at", name="hours_order"),
        Index("ix_masjids_location", "location", postgresql_using="gist"),
        Index("ix_masjids_state_city", "state", "city"),
    )

    name: Mapped[str] = mapped_column(Text)
    address_line1: Mapped[str] = mapped_column(Text)
    address_line2: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(
        Text, server_default=text("'Uttarakhand'")
    )
    postal_code: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str] = mapped_column(String(2), server_default=text("'IN'"))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    location: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(
        Text, server_default=text("'Asia/Kolkata'")
    )
    map_id: Mapped[str | None] = mapped_column(Text)

    accessible_by_public_transport: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    accessibility_details: Mapped[str | None] = mapped_column(Text)
    highway_masjid: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    on_road_masjid: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )

    opens_at: Mapped[time | None]
    closes_at: Mapped[time | None]
    is_24_hours: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    ramadan_adjusted_hours: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    has_wudu_stations: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    has_urinals: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    has_toilets: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    has_womens_prayer_area: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    has_library: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    has_parking: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    has_street_parking: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )

    other_items: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )

    schedules: Mapped[list["SalatSchedule"]] = relationship(
        back_populates="masjid",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    programs: Mapped[list["MasjidProgram"]] = relationship(
        back_populates="masjid",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    people: Mapped[list["MasjidPerson"]] = relationship(
        back_populates="masjid",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    photos: Mapped[list["MasjidPhoto"]] = relationship(
        back_populates="masjid",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    outbox_events: Mapped[list["OutboxEvent"]] = relationship(
        back_populates="masjid",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
