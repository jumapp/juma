"""Masjid photo model with storage and moderation.

This model stores photo metadata and handles file uploads to GCS or local storage.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.enums import PhotoModerationStatus, enum_values, ALLOWED_PHOTO_MIME_TYPES


class MasjidPhoto(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "masjid_photos"
    __table_args__ = (
        UniqueConstraint("id", "masjid_id", name="uq_photo_id_masjid"),
        CheckConstraint(
            "char_length(btrim(filename)) BETWEEN 1 AND 255",
            name="filename_length",
        ),
        CheckConstraint(
            "char_length(btrim(caption)) BETWEEN 1 AND 200",
            name="caption_length",
        ),
        CheckConstraint(
            "size >= 0 AND size <= 100000000", name="size_range"
        ),
        CheckConstraint(
            "width IS NULL OR width > 0", name="width_positive"
        ),
        CheckConstraint(
            "height IS NULL OR height > 0", name="height_positive"
        ),
        CheckConstraint(
            "(width IS NOT NULL AND height IS NOT NULL) OR (width IS NULL AND height IS NULL)",
            name="dimensions_both_or_none",
        ),
        CheckConstraint(
            "order_index >= 0", name="order_index_non_negative"
        ),
        Index(
            "ix_masjid_photos_scope",
            "masjid_id",
            "moderation_status",
            "is_featured",
            "order_index",
        ),
    )

    masjid_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("masjids.id", ondelete="CASCADE")
    )
    filename: Mapped[str] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(Text)
    size: Mapped[int] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(SmallInteger)
    height: Mapped[int | None] = mapped_column(SmallInteger)
    caption: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    is_featured: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false")
    )
    moderation_status: Mapped[PhotoModerationStatus] = mapped_column(
        Enum(
            PhotoModerationStatus,
            name="photo_moderation_status_values",
            native_enum=False,
            create_constraint=True,
            length=16,
            values_callable=enum_values,
        ),
        default=PhotoModerationStatus.PENDING,
        server_default=text("'pending'"),
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("masjid_people.id")
    )
    review_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    masjid: Mapped["Masjid"] = relationship(back_populates="photos")
    reviewer: Mapped["MasjidPerson"] = relationship(
        foreign_keys=[reviewer_id],
        uselist=False,
    )