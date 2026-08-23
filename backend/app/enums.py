"""Domain enumerations shared by models and API schemas."""

from enum import Enum


def enum_values(enum_cls) -> list[str]:
    return [member.value for member in enum_cls]


class SalatName(str, Enum):
    FAJR = "fajr"
    ZUHR = "zuhr"
    ASR = "asr"
    MAGHRIB = "maghrib"
    ISHA = "isha"
    JUMUAH = "jumuah"


SALAT_NAMES = [
    SalatName.FAJR,
    SalatName.ZUHR,
    SalatName.ASR,
    SalatName.MAGHRIB,
    SalatName.ISHA,
    SalatName.JUMUAH,
]


class AccessLevel(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    GENERAL = "general"
    VIEWER = "viewer"


class PersonRole(str, Enum):
    IMAM = "imam"
    MUZZIN = "muazzin"
    COMMITTEE_MEMBER = "committee_member"
    OTHER = "other"


class ProgramType(str, Enum):
    MAKTAB = "maktab"
    ELDER_MAKTAB = "elder_maktab"
    TAFSEER = "tafseer"
    HADITH = "hadith"
    OTHER_COURSE = "other_course"


class ScheduleFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PhotoModerationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


ALLOWED_PHOTO_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]