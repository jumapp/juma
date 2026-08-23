"""Masjid program, program schedule slots, and instructor models."""

import uuid
from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    Time,
    UniqueConstraint,
    text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.enums import ProgramType, ScheduleFrequency, enum_values


class MasjidProgram(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "masjid_programs"
    __table_args__ = (
        UniqueConstraint("id", "masjid_id", name="uq_program_id_masjid"),
        CheckConstraint(
            "char_length(btrim(name)) BETWEEN 1 AND 200", name="name_length"
        ),
        CheckConstraint(
            "max_participants IS NULL OR max_participants > 0",
            name="max_participants_positive",
        ),
        Index(
            "ix_masjid_programs_scope",
            "masjid_id",
            "type",
            "is_active",
        ),
    )

    masjid_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("masjids.id", ondelete="CASCADE")
    )
    type: Mapped[ProgramType] = mapped_column(
        Enum(
            ProgramType,
            name="program_type_values",
            native_enum=False,
            create_constraint=True,
            length=32,
            values_callable=enum_values,
        ),
    )
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    max_participants: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
    )

    masjid: Mapped["Masjid"] = relationship(back_populates="programs")
    schedules: Mapped[list["ProgramSchedule"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ProgramSchedule.start_time",
    )


class ProgramSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "program_schedules"
    __table_args__ = (
        CheckConstraint(
            "frequency <> 'weekly' OR weekday IS NOT NULL",
            name="weekly_requires_weekday",
        ),
        CheckConstraint(
            "frequency <> 'monthly' OR day_of_month IS NOT NULL",
            name="monthly_requires_day",
        ),
        CheckConstraint(
            "frequency <> 'daily' OR (weekday IS NULL AND day_of_month IS NULL)",
            name="daily_no_day",
        ),
        CheckConstraint(
            "weekday IS NULL OR weekday BETWEEN 0 AND 6", name="weekday_range"
        ),
        CheckConstraint(
            "day_of_month IS NULL OR day_of_month BETWEEN 1 AND 31",
            name="day_of_month_range",
        ),
        CheckConstraint("end_time > start_time", name="time_order"),
        Index("ix_program_schedules_program", "program_id", "weekday"),
    )

    program_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("masjid_programs.id", ondelete="CASCADE")
    )
    frequency: Mapped[ScheduleFrequency] = mapped_column(
        Enum(
            ScheduleFrequency,
            name="schedule_frequency_values",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=enum_values,
        ),
    )
    weekday: Mapped[int | None] = mapped_column(SmallInteger)
    day_of_month: Mapped[int | None] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    program: Mapped[MasjidProgram] = relationship(back_populates="schedules")


class ProgramInstructor(Base):
    """Association linking programs to instructors within the same masjid.

    The composite foreign keys guarantee a program and its instructor belong
    to the same masjid.
    """

    __tablename__ = "program_instructors"
    __table_args__ = (
        PrimaryKeyConstraint("program_id", "person_id"),
        ForeignKeyConstraint(
            ["program_id", "masjid_id"],
            ["masjid_programs.id", "masjid_programs.masjid_id"],
            ondelete="CASCADE",
            name="fk_program_instructors_program",
        ),
        ForeignKeyConstraint(
            ["person_id", "masjid_id"],
            ["masjid_people.id", "masjid_people.masjid_id"],
            ondelete="CASCADE",
            name="fk_program_instructors_person",
        ),
    )

    program_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
    masjid_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
