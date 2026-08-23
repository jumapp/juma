"""Pydantic schemas for request validation and OpenAPI documentation."""

from datetime import time, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from app.enums import (
    SalatName,
    AccessLevel,
    PersonRole,
    ProgramType,
    ScheduleFrequency,
    PhotoModerationStatus,
)


# ==========================================
# Masjid Schemas
# ==========================================

class MasjidCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the masjid",
        json_schema_extra={"example": "Jama Masjid Dehradun"}
    )
    address_line1: str = Field(
        ...,
        description="Primary address line",
        json_schema_extra={"example": "123 Main Street, Paltan Bazaar"}
    )
    address_line2: Optional[str] = Field(
        None,
        description="Secondary address line",
        json_schema_extra={"example": "Near Clock Tower"}
    )
    city: str = Field(
        ...,
        description="City name",
        json_schema_extra={"example": "Dehradun"}
    )
    state: str = Field(
        "Uttarakhand",
        description="State name",
        json_schema_extra={"example": "Uttarakhand"}
    )
    postal_code: Optional[str] = Field(
        None,
        description="Postal code",
        json_schema_extra={"example": "248001"}
    )
    country: str = Field(
        "IN",
        min_length=2,
        max_length=2,
        description="ISO 2-letter country code",
        json_schema_extra={"example": "IN"}
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude (-90 to 90)",
        json_schema_extra={"example": 30.3165}
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude (-180 to 180)",
        json_schema_extra={"example": 78.0322}
    )
    timezone: str = Field(
        "Asia/Kolkata",
        description="IANA Timezone string",
        json_schema_extra={"example": "Asia/Kolkata"}
    )
    map_id: Optional[str] = Field(
        None,
        description="Google Maps Place ID or external map reference",
        json_schema_extra={"example": "ChIJbU60yGQpEmsR1w28Z785f_U"}
    )
    accessible_by_public_transport: bool = Field(
        False,
        description="Whether accessible by public transport"
    )
    accessibility_details: Optional[str] = Field(
        None,
        description="Public transport access details"
    )
    highway_masjid: bool = Field(
        False,
        description="Whether located on/near a major highway"
    )
    on_road_masjid: bool = Field(
        False,
        description="Whether easily accessible directly from main road"
    )
    opens_at: Optional[str] = Field(
        None,
        description="Daily opening time (HH:MM:SS)",
        json_schema_extra={"example": "04:30:00"}
    )
    closes_at: Optional[str] = Field(
        None,
        description="Daily closing time (HH:MM:SS)",
        json_schema_extra={"example": "22:00:00"}
    )
    is_24_hours: bool = Field(
        False,
        description="Whether open 24 hours"
    )
    ramadan_adjusted_hours: Optional[Dict[str, Any]] = Field(
        None,
        description="Adjusted operating hours during Ramadan"
    )
    has_wudu_stations: bool = Field(False, description="Wudu facilities available")
    has_urinals: bool = Field(False, description="Urinals available")
    has_toilets: bool = Field(False, description="Toilets available")
    has_womens_prayer_area: bool = Field(False, description="Dedicated women prayer area")
    has_library: bool = Field(False, description="Library available")
    has_parking: bool = Field(False, description="On-site parking available")
    has_street_parking: bool = Field(False, description="Street parking available")
    other_items: Optional[str] = Field(None, description="Other facilities or remarks")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata JSON")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jama Masjid Dehradun",
                "address_line1": "123 Main Street, Paltan Bazaar",
                "address_line2": "Near Clock Tower",
                "city": "Dehradun",
                "state": "Uttarakhand",
                "postal_code": "248001",
                "country": "IN",
                "latitude": 30.3165,
                "longitude": 78.0322,
                "timezone": "Asia/Kolkata",
                "accessible_by_public_transport": True,
                "highway_masjid": False,
                "on_road_masjid": True,
                "opens_at": "04:30:00",
                "closes_at": "22:00:00",
                "is_24_hours": False,
                "has_wudu_stations": True,
                "has_toilets": True,
                "has_womens_prayer_area": True,
                "has_parking": True,
                "meta": {}
            }
        }
    )


class MasjidUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    timezone: Optional[str] = None
    map_id: Optional[str] = None
    accessible_by_public_transport: Optional[bool] = None
    accessibility_details: Optional[str] = None
    highway_masjid: Optional[bool] = None
    on_road_masjid: Optional[bool] = None
    opens_at: Optional[str] = None
    closes_at: Optional[str] = None
    is_24_hours: Optional[bool] = None
    ramadan_adjusted_hours: Optional[Dict[str, Any]] = None
    has_wudu_stations: Optional[bool] = None
    has_urinals: Optional[bool] = None
    has_toilets: Optional[bool] = None
    has_womens_prayer_area: Optional[bool] = None
    has_library: Optional[bool] = None
    has_parking: Optional[bool] = None
    has_street_parking: Optional[bool] = None
    other_items: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Jama Masjid Dehradun",
                "has_womens_prayer_area": True,
                "has_parking": True
            }
        }
    )


# ==========================================
# Salat Schedule Schemas
# ==========================================

class SalatScheduleCreate(BaseModel):
    masjid_id: UUID = Field(
        ...,
        description="ID of the associated masjid",
        json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"}
    )
    salat_name: SalatName = Field(
        ...,
        description="Name of the salat (fajr, dhuhr, asr, maghrib, isha, jumuah)",
        json_schema_extra={"example": "fajr"}
    )
    adhan_time: Optional[str] = Field(
        None,
        description="Adhan time (HH:MM:SS)",
        json_schema_extra={"example": "05:00:00"}
    )
    iqama_time: str = Field(
        ...,
        description="Iqama time (HH:MM:SS)",
        json_schema_extra={"example": "05:30:00"}
    )
    khutbah_time: Optional[str] = Field(
        None,
        description="Khutbah time for Jumuah (HH:MM:SS)",
        json_schema_extra={"example": "13:15:00"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "masjid_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "salat_name": "fajr",
                "adhan_time": "05:00:00",
                "iqama_time": "05:30:00"
            }
        }
    )


class SalatScheduleUpdate(BaseModel):
    adhan_time: Optional[str] = Field(None, description="Adhan time (HH:MM:SS)")
    iqama_time: Optional[str] = Field(None, description="Iqama time (HH:MM:SS)")
    khutbah_time: Optional[str] = Field(None, description="Khutbah time (HH:MM:SS)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "adhan_time": "05:05:00",
                "iqama_time": "05:35:00"
            }
        }
    )


# ==========================================
# Program Schemas
# ==========================================

class ProgramCreate(BaseModel):
    masjid_id: UUID = Field(
        ...,
        description="ID of the associated masjid",
        json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"}
    )
    type: ProgramType = Field(
        ...,
        description="Program type",
        json_schema_extra={"example": "quran_class"}
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Program name",
        json_schema_extra={"example": "Weekly Tafseer Study"}
    )
    description: Optional[str] = Field(
        None,
        description="Program description",
        json_schema_extra={"example": "Detailed commentary on Surah Yaseen after Maghrib"}
    )
    max_participants: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum participants allowed",
        json_schema_extra={"example": 50}
    )
    is_active: bool = Field(True, description="Whether program is active")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "masjid_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "type": "quran_class",
                "name": "Weekly Tafseer Study",
                "description": "Detailed commentary after Maghrib every Friday",
                "max_participants": 50,
                "is_active": True
            }
        }
    )


class ProgramUpdate(BaseModel):
    type: Optional[ProgramType] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    max_participants: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Advanced Quran & Hadith Study",
                "max_participants": 75,
                "is_active": True
            }
        }
    )


# ==========================================
# Person Schemas
# ==========================================

class PersonCreate(BaseModel):
    masjid_id: UUID = Field(
        ...,
        description="ID of the associated masjid",
        json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"}
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name",
        json_schema_extra={"example": "Sheikh Ahmad Ali"}
    )
    role: PersonRole = Field(
        ...,
        description="Role in masjid",
        json_schema_extra={"example": "imam"}
    )
    access_level: AccessLevel = Field(
        AccessLevel.VIEWER,
        description="System access level",
        json_schema_extra={"example": "editor"}
    )
    phone_primary: Optional[str] = Field(
        None,
        description="Primary phone number",
        json_schema_extra={"example": "+919876543210"}
    )
    phone_alternate: Optional[str] = Field(
        None,
        description="Alternate phone number",
        json_schema_extra={"example": "+919876543211"}
    )
    email: Optional[str] = Field(
        None,
        description="Email address",
        json_schema_extra={"example": "ahmad.ali@example.com"}
    )
    skills: Optional[str] = Field(
        None,
        description="Skills or qualifications",
        json_schema_extra={"example": "Tajweed, Fiqh, Youth Counseling"}
    )
    bio: Optional[str] = Field(
        None,
        description="Short bio",
        json_schema_extra={"example": "Graduate of Al-Azhar University"}
    )
    photo_url: Optional[str] = Field(
        None,
        description="Photo URL",
        json_schema_extra={"example": "https://example.com/photos/ahmad.jpg"}
    )
    is_active: bool = Field(True, description="Active status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "masjid_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "full_name": "Sheikh Ahmad Ali",
                "role": "imam",
                "access_level": "editor",
                "phone_primary": "+919876543210",
                "email": "ahmad.ali@example.com",
                "skills": "Tajweed, Fiqh",
                "bio": "Lead Imam since 2018",
                "is_active": True
            }
        }
    )


class PersonUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[PersonRole] = None
    access_level: Optional[AccessLevel] = None
    phone_primary: Optional[str] = None
    phone_alternate: Optional[str] = None
    email: Optional[str] = None
    skills: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "imam",
                "phone_primary": "+919876543210",
                "bio": "Updated biography details"
            }
        }
    )


# ==========================================
# Photo Schemas
# ==========================================

class PhotoUpload(BaseModel):
    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original photo filename",
        json_schema_extra={"example": "masjid_front.jpg"}
    )
    file_path: str = Field(
        ...,
        description="Storage path or URI",
        json_schema_extra={"example": "uploads/masjids/masjid_front.jpg"}
    )
    mime_type: str = Field(
        ...,
        description="MIME type (image/jpeg, image/png, image/webp)",
        json_schema_extra={"example": "image/jpeg"}
    )
    size: int = Field(
        ...,
        ge=0,
        le=100000000,
        description="File size in bytes",
        json_schema_extra={"example": 1048576}
    )
    width: Optional[int] = Field(
        None,
        gt=0,
        description="Image width in pixels",
        json_schema_extra={"example": 1920}
    )
    height: Optional[int] = Field(
        None,
        gt=0,
        description="Image height in pixels",
        json_schema_extra={"example": 1080}
    )
    caption: Optional[str] = Field(
        None,
        max_length=200,
        description="Photo caption",
        json_schema_extra={"example": "Main entrance view of Jama Masjid"}
    )
    order_index: int = Field(
        0,
        ge=0,
        description="Display order index",
        json_schema_extra={"example": 0}
    )
    is_featured: bool = Field(False, description="Whether featured photo")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "masjid_front.jpg",
                "file_path": "uploads/masjids/masjid_front.jpg",
                "mime_type": "image/jpeg",
                "size": 1048576,
                "width": 1920,
                "height": 1080,
                "caption": "Main entrance view of Jama Masjid",
                "order_index": 0,
                "is_featured": True
            }
        }
    )


# ==========================================
# Sync Schemas
# ==========================================

class MutationItem(BaseModel):
    id: str = Field(..., description="Client mutation ID")
    entity: str = Field(..., description="Target entity type (masjid, salat_schedule, program, person)")
    type: str = Field(..., description="Mutation type (CREATE, UPDATE, DELETE)")
    payload: Dict[str, Any] = Field(..., description="Entity payload data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "mut-12345",
                "entity": "masjid",
                "type": "CREATE",
                "payload": {
                    "name": "Offline Masjid Test",
                    "address_line1": "Road 1",
                    "city": "Dehradun",
                    "state": "Uttarakhand",
                    "country": "IN",
                    "latitude": 30.3165,
                    "longitude": 78.0322,
                    "timezone": "Asia/Kolkata"
                }
            }
        }
    )


class SyncMutationsRequest(BaseModel):
    mutations: List[MutationItem] = Field(
        ...,
        description="List of client offline mutations to process"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mutations": [
                    {
                        "id": "mut-12345",
                        "entity": "masjid",
                        "type": "CREATE",
                        "payload": {
                            "name": "Offline Masjid Test",
                            "address_line1": "Road 1",
                            "city": "Dehradun",
                            "state": "Uttarakhand",
                            "country": "IN",
                            "latitude": 30.3165,
                            "longitude": 78.0322,
                            "timezone": "Asia/Kolkata"
                        }
                    }
                ]
            }
        }
    )


# ==========================================
# Admin Schemas
# ==========================================

class RoleRequestUpdate(BaseModel):
    status: str = Field(
        ...,
        description="New request status ('approved' or 'rejected')",
        json_schema_extra={"example": "approved"}
    )
    reason: Optional[str] = Field(
        None,
        description="Reason or notes for decision",
        json_schema_extra={"example": "Verified identity and committee membership"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "approved",
                "reason": "Verified identity and committee membership"
            }
        }
    )


# ==========================================
# Response Schemas
# ==========================================

class MasjidResponse(BaseModel):
    id: str = Field(..., description="Masjid UUID", json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"})
    name: str = Field(..., description="Name of the masjid", json_schema_extra={"example": "Jama Masjid Dehradun"})
    address_line1: str = Field(..., json_schema_extra={"example": "123 Main Street, Paltan Bazaar"})
    address_line2: Optional[str] = Field(None, json_schema_extra={"example": "Near Clock Tower"})
    city: str = Field(..., json_schema_extra={"example": "Dehradun"})
    state: str = Field("Uttarakhand", json_schema_extra={"example": "Uttarakhand"})
    postal_code: Optional[str] = Field(None, json_schema_extra={"example": "248001"})
    country: str = Field("IN", json_schema_extra={"example": "IN"})
    latitude: float = Field(..., json_schema_extra={"example": 30.3165})
    longitude: float = Field(..., json_schema_extra={"example": 78.0322})
    timezone: str = Field("Asia/Kolkata", json_schema_extra={"example": "Asia/Kolkata"})
    created_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})
    updated_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})


class SalatScheduleResponse(BaseModel):
    id: str = Field(..., description="Schedule UUID", json_schema_extra={"example": "b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22"})
    masjid_id: str = Field(..., description="Masjid UUID", json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"})
    salat_name: str = Field(..., json_schema_extra={"example": "fajr"})
    adhan_time: Optional[str] = Field(None, json_schema_extra={"example": "05:00:00"})
    iqama_time: str = Field(..., json_schema_extra={"example": "05:30:00"})
    khutbah_time: Optional[str] = Field(None, json_schema_extra={"example": None})
    created_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})
    updated_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})


class ProgramResponse(BaseModel):
    id: str = Field(..., description="Program UUID", json_schema_extra={"example": "c2ffbc99-9c0b-4ef8-bb6d-6bb9bd380a33"})
    masjid_id: str = Field(..., description="Masjid UUID", json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"})
    type: str = Field(..., json_schema_extra={"example": "quran_class"})
    name: str = Field(..., json_schema_extra={"example": "Weekly Tafseer Study"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Detailed commentary after Maghrib"})
    max_participants: Optional[int] = Field(None, json_schema_extra={"example": 50})
    is_active: bool = Field(True)
    created_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})
    updated_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})


class PersonResponse(BaseModel):
    id: str = Field(..., description="Person UUID", json_schema_extra={"example": "d3ffbc99-9c0b-4ef8-bb6d-6bb9bd380a44"})
    masjid_id: str = Field(..., description="Masjid UUID", json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"})
    full_name: str = Field(..., json_schema_extra={"example": "Sheikh Ahmad Ali"})
    role: str = Field(..., json_schema_extra={"example": "imam"})
    access_level: str = Field(..., json_schema_extra={"example": "editor"})
    phone_primary: Optional[str] = Field(None, json_schema_extra={"example": "+919876543210"})
    phone_alternate: Optional[str] = Field(None)
    email: Optional[str] = Field(None, json_schema_extra={"example": "ahmad.ali@example.com"})
    skills: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)
    photo_url: Optional[str] = Field(None)
    is_active: bool = Field(True)
    created_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})
    updated_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})


class PhotoResponse(BaseModel):
    id: str = Field(..., description="Photo UUID", json_schema_extra={"example": "e4ffbc99-9c0b-4ef8-bb6d-6bb9bd380a55"})
    masjid_id: str = Field(..., description="Masjid UUID", json_schema_extra={"example": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"})
    filename: str = Field(..., json_schema_extra={"example": "masjid_front.jpg"})
    file_path: str = Field(..., json_schema_extra={"example": "uploads/masjids/masjid_front.jpg"})
    mime_type: str = Field(..., json_schema_extra={"example": "image/jpeg"})
    size: int = Field(..., json_schema_extra={"example": 1048576})
    width: Optional[int] = Field(None, json_schema_extra={"example": 1920})
    height: Optional[int] = Field(None, json_schema_extra={"example": 1080})
    caption: Optional[str] = Field(None, json_schema_extra={"example": "Main entrance view"})
    order_index: int = Field(0)
    is_featured: bool = Field(False)
    moderation_status: str = Field("pending")
    review_reason: Optional[str] = Field(None)
    created_at: Optional[str] = Field(None, json_schema_extra={"example": "2026-08-23T12:00:00Z"})


class DeleteResponse(BaseModel):
    id: str = Field(..., description="Deleted item UUID")
    status: str = Field("deleted", description="Deletion status")

