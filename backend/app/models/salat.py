"""Salat schedule model (one row per masjid and salat)."""

import uuid
from datetime import time

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.enums import SalatName, enum_values, SALAT_NAMES


class SalatSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "salat_schedules"
    __table_args__ = (
        UniqueConstraint("masjid_id", "salat_name", name="uq_masjid_salat"),
        CheckConstraint(
            "khutbah_time IS NULL OR salat_name = 'jumuah'",
            name="khutbah_jumuah_only",
        ),
        CheckConstraint(
            "adhan_time IS NULL OR iqama_time >= adhan_time",
            name="iqama_after_adhan",
        ),
        Index("ix_salat_schedules_masjid", "masjid_id"),
    )

    masjid_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("masjids.id", ondelete="CASCADE")
    )
    salat_name: Mapped[SalatName] = mapped_column(
        Enum(
            SalatName,
            name="salat_name_values",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=enum_values,
        ),
    )
    adhan_time: Mapped[time | None] = mapped_column(Time)
    iqama_time: Mapped[time] = mapped_column(Time, nullable=False)
    khutbah_time: Mapped[time | None] = mapped_column(Time)

    masjid: Mapped["Masjid"] = relationship(back_populates="schedules")
