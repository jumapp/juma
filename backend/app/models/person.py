"""Masjid person (imam, muazzin, committee member) model."""

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.enums import AccessLevel, PersonRole, enum_values

_PHONE_PATTERN = "^[+]?[0-9][0-9 ()-]{5,19}$"


class MasjidPerson(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "masjid_people"
    __table_args__ = (
        UniqueConstraint("id", "masjid_id", name="uq_person_id_masjid"),
        CheckConstraint(
            "char_length(btrim(full_name)) BETWEEN 1 AND 200",
            name="full_name_length",
        ),
        CheckConstraint(
            f"phone_primary IS NULL OR phone_primary ~ '{_PHONE_PATTERN}'",
            name="phone_primary_format",
        ),
        CheckConstraint(
            f"phone_alternate IS NULL OR phone_alternate ~ '{_PHONE_PATTERN}'",
            name="phone_alternate_format",
        ),
        CheckConstraint(
            "email IS NULL OR email LIKE '%_@_%._%'",
            name="email_format",
        ),
        Index(
            "ix_masjid_people_scope",
            "masjid_id",
            "role",
            "access_level",
            "is_active",
        ),
    )

    masjid_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("masjids.id", ondelete="CASCADE")
    )
    full_name: Mapped[str] = mapped_column(Text)
    role: Mapped[PersonRole] = mapped_column(
        Enum(
            PersonRole,
            name="person_role_values",
            native_enum=False,
            create_constraint=True,
            length=32,
            values_callable=enum_values,
        ),
    )
    access_level: Mapped[AccessLevel] = mapped_column(
        Enum(
            AccessLevel,
            name="access_level_values",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=enum_values,
        ),
        default=AccessLevel.VIEWER,
        server_default=text("'viewer'"),
    )
    phone_primary: Mapped[str | None] = mapped_column(Text)
    phone_alternate: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true")
    )

    masjid: Mapped["Masjid"] = relationship(back_populates="people")
