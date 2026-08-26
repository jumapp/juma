"""Services layer for business logic.

This layer implements the business logic of the application,
using repositories for data access and implementing validation,
authorization, and domain rules.
"""

import uuid
from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.enums import (
    SalatName, AccessLevel, PersonRole, ProgramType, 
    ScheduleFrequency, PhotoModerationStatus, SALAT_NAMES
)
from app.repositories import (
    MasjidRepository, SalatScheduleRepository, PersonRepository,
    ProgramRepository, PhotoRepository, AuditRepository, OutboxRepository
)
from app.models.masjid import Masjid
from app.models.salat import SalatSchedule
from app.models.person import MasjidPerson
from app.models.program import MasjidProgram, ProgramSchedule
from app.models.photo import MasjidPhoto
from app.models.audit import AuditEvent, AuditAction
from app.models.outbox import OutboxEvent
from app.services.photo_service import get_photo_storage_service


def _json_safe(value: Any, key: str | None = None) -> Any:
    """Convert audit state values to JSON-compatible values."""
    if key == "location":
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, time)):
        return value.isoformat()
    if isinstance(value, (uuid.UUID, Enum)):
        return str(value.value if isinstance(value, Enum) else value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {
            item_key: _json_safe(item_value, item_key)
            for item_key, item_value in value.items()
            if item_key != "location"
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


class BaseService:
    """Base service with common business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.masjid_repo = MasjidRepository(session)
        self.salat_repo = SalatScheduleRepository(session)
        self.person_repo = PersonRepository(session)
        self.program_repo = ProgramRepository(session)
        self.photo_repo = PhotoRepository(session)
        self.audit_repo = AuditRepository(session)
        self.outbox_repo = OutboxRepository(session)

    def _create_audit_event(
        self,
        actor_id: uuid.UUID,
        actor_type: str,
        action: AuditAction,
        entity_type: str,
        entity_id: uuid.UUID,
        before_state: Dict[str, Any] = None,
        after_state: Dict[str, Any] = None,
        reason: str = None,
        request_id: str = None
    ) -> AuditEvent:
        """Create an audit event."""
        return AuditEvent.from_change(
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=_json_safe(before_state),
            after_state=_json_safe(after_state),
            reason=reason,
            request_id=request_id
        )

    def _publish_outbox_event(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        event_data: Dict[str, Any],
        masjid_id: uuid.UUID = None
    ):
        """Publish an event to the outbox."""
        event = OutboxEvent(
            id=uuid.uuid4(),
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_data=event_data,
            masjid_id=masjid_id
        )
        self.session.add(event)


class MasjidService(BaseService):
    """Service for masjid business logic."""

    async def create_masjid(
        self,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> Masjid:
        """Create a new masjid."""
        # Validate required fields
        required_fields = ["name", "address_line1", "city", "state", "country", 
                          "latitude", "longitude", "timezone"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate coordinates
        lat, lon = data["latitude"], data["longitude"]
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        # Convert to GeoAlchemy2 point
        from geoalchemy2.elements import WKBElement
        from geoalchemy2.shape import from_shape
        from shapely.geometry import Point
        import pyproj
        
        location = from_shape(
            Point(lon, lat), 
            srid=4326
        )
        data["location"] = location
        
        # Set default values
        if "state" not in data:
            data["state"] = "Uttarakhand"
        if "country" not in data:
            data["country"] = "IN"
        if "timezone" not in data:
            data["timezone"] = "Asia/Kolkata"
        
        # Create masjid
        masjid = await self.masjid_repo.create(Masjid, data)
        
        # Create default salat schedules
        default_iqama_times = {
            SalatName.FAJR: "05:30",
            SalatName.ZUHR: "13:00",
            SalatName.ASR: "16:30",
            SalatName.MAGHRIB: "18:30",
            SalatName.ISHA: "20:00",
            SalatName.JUMUAH: "13:00"
        }
        
        for salat_name in SALAT_NAMES:
            salat_time = time.fromisoformat(default_iqama_times.get(salat_name, "12:00"))
            
            schedule_data = {
                "masjid_id": masjid.id,
                "salat_name": salat_name,
                "iqama_time": salat_time
            }
            
            await self.salat_repo.create(SalatSchedule, schedule_data)
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="masjid_editor",
            action=AuditAction.CREATE,
            entity_type="masjid",
            entity_id=masjid.id,
            after_state=data,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid.id),
            "name": data["name"],
            "location": f"{lat},{lon}",
            "action": "create"
        }
        
        self._publish_outbox_event(
            event_type="masjid_created",
            aggregate_type="masjid",
            aggregate_id=masjid.id,
            event_data=outbox_event_data,
            masjid_id=masjid.id
        )
        
        await self.masjid_repo.commit()
        return masjid

    async def update_masjid(
        self,
        masjid_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> Optional[Masjid]:
        """Update an existing masjid."""
        # Get existing masjid
        existing_masjid = await self.masjid_repo.get_by_id(Masjid, masjid_id)
        if not existing_masjid:
            return None
        
        # Store before state for audit
        before_state = {
            field: getattr(existing_masjid, field)
            for field in existing_masjid.__table__.columns.keys()
            if hasattr(existing_masjid, field)
        }
        
        # Update fields
        for key, value in data.items():
            if hasattr(existing_masjid, key):
                setattr(existing_masjid, key, value)
        
        # Validate coordinates if updated
        if "latitude" in data or "longitude" in data:
            lat = data.get("latitude", getattr(existing_masjid, "latitude"))
            lon = data.get("longitude", getattr(existing_masjid, "longitude"))
            
            if not (-90 <= lat <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= lon <= 180):
                raise ValueError("Longitude must be between -180 and 180")
            
            # Update location
            from shapely.geometry import Point
            from geoalchemy2.shape import from_shape
            
            location = from_shape(Point(lon, lat), srid=4326)
            existing_masjid.location = location
        
        # Update audit event
        after_state = {
            field: getattr(existing_masjid, field)
            for field in existing_masjid.__table__.columns.keys()
            if hasattr(existing_masjid, field)
        }
        
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="masjid_editor",
            action=AuditAction.UPDATE,
            entity_type="masjid",
            entity_id=masjid_id,
            before_state=before_state,
            after_state=after_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "updates": data,
            "action": "update"
        }
        
        self._publish_outbox_event(
            event_type="masjid_updated",
            aggregate_type="masjid",
            aggregate_id=masjid_id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        await self.masjid_repo.commit()
        await self.masjid_repo.refresh(existing_masjid)
        return existing_masjid

    async def get_masjid(
        self,
        masjid_id: uuid.UUID,
        include_related: bool = True
    ) -> Optional[Masjid]:
        """Get a masjid by ID."""
        options = []
        if include_related:
            options = [
                joinedload(Masjid.schedules),
                joinedload(Masjid.programs),
                joinedload(Masjid.people),
                joinedload(Masjid.photos),
                joinedload(Masjid.audit_events)
            ]
        
        return await self.masjid_repo.get_by_id(Masjid, masjid_id, options)

    async def list_masjids(
        self,
        lat: float = None,
        lon: float = None,
        radius: int = 2000,
        city: str = None,
        state: str = None,
        accessible_by_transport: bool = None,
        include_related: bool = True
    ) -> List[Masjid]:
        """List masjids with optional filters."""
        options = []
        if include_related:
            options = [
                joinedload(Masjid.schedules),
                joinedload(Masjid.programs),
                joinedload(Masjid.people),
                joinedload(Masjid.photos)
            ]
        
        return await self.masjid_repo.get_by_filters(
            lat=lat,
            lon=lon,
            radius=radius,
            city=city,
            state=state,
            accessible_by_transport=accessible_by_transport,
            options=options
        )

    async def delete_masjid(
        self,
        masjid_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> bool:
        """Delete a masjid."""
        masjid = await self.get_masjid(masjid_id, include_related=False)
        if not masjid:
            return False
        
        # Store before state for audit
        before_state = {
            field: getattr(masjid, field)
            for field in masjid.__table__.columns.keys()
            if hasattr(masjid, field)
        }
        
        # Delete audit events first
        await self.audit_repo.get_all(AuditEvent, filters={"entity_id": masjid_id})
        # Note: CASCADE DELETE will handle related records
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="masjid_editor",
            action=AuditAction.DELETE,
            entity_type="masjid",
            entity_id=masjid_id,
            before_state=before_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "action": "delete"
        }
        
        self._publish_outbox_event(
            event_type="masjid_deleted",
            aggregate_type="masjid",
            aggregate_id=masjid_id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        # Delete the masjid (CASCADE will handle related records)
        await self.masjid_repo.delete(Masjid, masjid_id)
        await self.masjid_repo.commit()
        return True


class SalatScheduleService(BaseService):
    """Service for salat schedule business logic."""

    async def create_schedule(
        self,
        masjid_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> SalatSchedule:
        """Create a new salat schedule."""
        # Validate salat name
        if data["salat_name"] not in SALAT_NAMES:
            raise ValueError(f"Invalid salat name: {data['salat_name']}")
        
        # Validate times
        adhan_time = data.get("adhan_time")
        iqama_time = data["iqama_time"]
        
        if adhan_time and iqama_time and adhan_time >= iqama_time:
            raise ValueError("Iqama time must be after adhan time")
        
        # Validate khutbah only for jumuah
        if data["salat_name"] != SalatName.JUMUAH and data.get("khutbah_time"):
            raise ValueError("Khutbah time can only be set for Jumuah salat")
        
        # Create schedule
        schedule = await self.salat_repo.create(SalatSchedule, data)
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="salat_editor",
            action=AuditAction.CREATE,
            entity_type="salat_schedule",
            entity_id=schedule.id,
            after_state=data,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "salat_name": data["salat_name"],
            "iqama_time": str(data["iqama_time"]),
            "action": "create"
        }
        
        self._publish_outbox_event(
            event_type="salat_schedule_created",
            aggregate_type="salat_schedule",
            aggregate_id=schedule.id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        await self.salat_repo.commit()
        return schedule

    async def update_schedule(
        self,
        schedule_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> Optional[SalatSchedule]:
        """Update an existing salat schedule."""
        # Get existing schedule
        existing = await self.salat_repo.get_by_id(SalatSchedule, schedule_id)
        if not existing:
            return None
        
        # Store before state
        before_state = {
            field: getattr(existing, field)
            for field in existing.__table__.columns.keys()
            if hasattr(existing, field)
        }
        
        # Update fields
        for key, value in data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        
        # Validate times if updated
        adhan_time = data.get("adhan_time", getattr(existing, "adhan_time"))
        iqama_time = data.get("iqama_time", getattr(existing, "iqama_time"))
        
        if adhan_time and iqama_time and adhan_time >= iqama_time:
            raise ValueError("Iqama time must be after adhan time")
        
        # Validate khutbah only for jumuah
        salat_name = data.get("salat_name", getattr(existing, "salat_name"))
        if salat_name != SalatName.JUMUAH and data.get("khutbah_time"):
            raise ValueError("Khutbah time can only be set for Jumuah salat")
        
        # Update audit event
        after_state = {
            field: getattr(existing, field)
            for field in existing.__table__.columns.keys()
            if hasattr(existing, field)
        }
        
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="salat_editor",
            action=AuditAction.UPDATE,
            entity_type="salat_schedule",
            entity_id=schedule_id,
            before_state=before_state,
            after_state=after_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "schedule_id": str(schedule_id),
            "updates": data,
            "action": "update"
        }
        
        self._publish_outbox_event(
            event_type="salat_schedule_updated",
            aggregate_type="salat_schedule",
            aggregate_id=schedule_id,
            event_data=outbox_event_data
        )
        
        await self.salat_repo.commit()
        await self.salat_repo.refresh(existing)
        return existing

    async def get_schedule(self, schedule_id: uuid.UUID) -> Optional[SalatSchedule]:
        """Get a salat schedule by ID."""
        return await self.salat_repo.get_by_id(SalatSchedule, schedule_id)

    async def delete_schedule(
        self,
        schedule_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> bool:
        """Delete a salat schedule."""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        # Store before state
        before_state = {
            field: getattr(schedule, field)
            for field in schedule.__table__.columns.keys()
            if hasattr(schedule, field)
        }
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="salat_editor",
            action=AuditAction.DELETE,
            entity_type="salat_schedule",
            entity_id=schedule_id,
            before_state=before_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "schedule_id": str(schedule_id),
            "action": "delete"
        }
        
        self._publish_outbox_event(
            event_type="salat_schedule_deleted",
            aggregate_type="salat_schedule",
            aggregate_id=schedule_id,
            event_data=outbox_event_data
        )
        
        # Delete the schedule
        await self.salat_repo.delete(SalatSchedule, schedule_id)
        await self.salat_repo.commit()
        return True


class PersonService(BaseService):
    """Service for MasjidPerson business logic."""

    async def create_person(
        self,
        masjid_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> MasjidPerson:
        """Create a new person (committee member)."""
        # Validate required fields
        required_fields = ["full_name", "role", "access_level"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate role
        if data["role"] not in [role.value for role in PersonRole]:
            raise ValueError(f"Invalid role: {data['role']}")
        
        # Validate access level
        if data["access_level"] not in [level.value for level in AccessLevel]:
            raise ValueError(f"Invalid access level: {data['access_level']}")
        
        # Validate phone format if provided
        phone_pattern = r"^\+?\d[\d ()-]{5,19}$"
        if "phone_primary" in data and data["phone_primary"]:
            import re
            if not re.match(phone_pattern, data["phone_primary"]):
                raise ValueError("Invalid phone number format")
        
        # Validate email if provided
        if "email" in data and data["email"]:
            email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
            import re
            if not re.match(email_pattern, data["email"]):
                raise ValueError("Invalid email format")
        
        # Set masjid_id
        data["masjid_id"] = masjid_id
        data["is_active"] = True
        
        # Create person
        person = await self.person_repo.create(MasjidPerson, data)
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="masjid_editor",
            action=AuditAction.CREATE,
            entity_type="person",
            entity_id=person.id,
            after_state=data,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "person_id": str(person.id),
            "full_name": data["full_name"],
            "role": data["role"],
            "action": "create"
        }
        
        self._publish_outbox_event(
            event_type="person_created",
            aggregate_type="person",
            aggregate_id=person.id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        await self.person_repo.commit()
        return person

    async def update_person(
        self,
        person_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> Optional[MasjidPerson]:
        """Update an existing person."""
        # Get existing person
        existing = await self.person_repo.get_by_id(MasjidPerson, person_id)
        if not existing:
            return None
        
        # Store before state
        before_state = {
            field: getattr(existing, field)
            for field in existing.__table__.columns.keys()
            if hasattr(existing, field)
        }
        
        # Validate role if updating
        if "role" in data:
            if data["role"] not in [role.value for role in PersonRole]:
                raise ValueError(f"Invalid role: {data['role']}")
        
        # Validate access level if updating
        if "access_level" in data:
            if data["access_level"] not in [level.value for level in AccessLevel]:
                raise ValueError(f"Invalid access level: {data['access_level']}")
        
        # Update fields
        for key, value in data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        
        # Update audit event
        after_state = {
            field: getattr(existing, field)
            for field in existing.__table__.columns.keys()
            if hasattr(existing, field)
        }
        
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="masjid_editor",
            action=AuditAction.UPDATE,
            entity_type="person",
            entity_id=person_id,
            before_state=before_state,
            after_state=after_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "person_id": str(person_id),
            "updates": data,
            "action": "update"
        }
        
        self._publish_outbox_event(
            event_type="person_updated",
            aggregate_type="person",
            aggregate_id=person_id,
            event_data=outbox_event_data
        )
        
        await self.person_repo.commit()
        await self.person_repo.refresh(existing)
        return existing

    async def delete_person(
        self,
        person_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> bool:
        """Delete a person."""
        person = await self.person_repo.get_by_id(MasjidPerson, person_id)
        if not person:
            return False
        
        # Store before state
        before_state = {
            field: getattr(person, field)
            for field in person.__table__.columns.keys()
            if hasattr(person, field)
        }
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="masjid_editor",
            action=AuditAction.DELETE,
            entity_type="person",
            entity_id=person_id,
            before_state=before_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "person_id": str(person_id),
            "action": "delete"
        }
        
        self._publish_outbox_event(
            event_type="person_deleted",
            aggregate_type="person",
            aggregate_id=person_id,
            event_data=outbox_event_data
        )
        
        # Delete the person
        await self.person_repo.delete(MasjidPerson, person_id)
        await self.person_repo.commit()
        return True

    async def get_person(self, person_id: uuid.UUID) -> Optional[MasjidPerson]:
        """Get a person by ID."""
        return await self.person_repo.get_by_id(MasjidPerson, person_id)

    async def get_persons_by_masjid(
        self,
        masjid_id: uuid.UUID,
        role: str = None,
        access_level: str = None,
        is_active: bool = None
    ) -> List[MasjidPerson]:
        """Get people for a masjid with optional filters."""
        return await self.person_repo.get_by_masjid(
            masjid_id, role=role, access_level=access_level, is_active=is_active
        )


class ProgramService(BaseService):
    """Service for MasjidProgram business logic."""

    async def create_program(
        self,
        masjid_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> MasjidProgram:
        """Create a new program."""
        # Validate required fields
        required_fields = ["type", "name"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate program type
        if data["type"] not in [pt.value for pt in ProgramType]:
            raise ValueError(f"Invalid program type: {data['type']}")
        
        # Validate max_participants if provided
        if "max_participants" in data and data["max_participants"] is not None:
            if data["max_participants"] <= 0:
                raise ValueError("max_participants must be greater than 0")
        
        # Set masjid_id
        data["masjid_id"] = masjid_id
        data["is_active"] = True
        
        # Create program
        program = await self.program_repo.create(MasjidProgram, data)
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="program_editor",
            action=AuditAction.CREATE,
            entity_type="program",
            entity_id=program.id,
            after_state=data,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "program_id": str(program.id),
            "type": data["type"],
            "name": data["name"],
            "action": "create"
        }
        
        self._publish_outbox_event(
            event_type="program_created",
            aggregate_type="program",
            aggregate_id=program.id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        await self.program_repo.commit()
        return program

    async def update_program(
        self,
        program_id: uuid.UUID,
        data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> Optional[MasjidProgram]:
        """Update an existing program."""
        # Get existing program
        existing = await self.program_repo.get_by_id(MasjidProgram, program_id)
        if not existing:
            return None
        
        # Store before state
        before_state = {
            field: getattr(existing, field)
            for field in existing.__table__.columns.keys()
            if hasattr(existing, field)
        }
        
        # Validate program type if updating
        if "type" in data:
            if data["type"] not in [pt.value for pt in ProgramType]:
                raise ValueError(f"Invalid program type: {data['type']}")
        
        # Validate max_participants if updating
        if "max_participants" in data and data["max_participants"] is not None:
            if data["max_participants"] <= 0:
                raise ValueError("max_participants must be greater than 0")
        
        # Update fields
        for key, value in data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        
        # Update audit event
        after_state = {
            field: getattr(existing, field)
            for field in existing.__table__.columns.keys()
            if hasattr(existing, field)
        }
        
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="program_editor",
            action=AuditAction.UPDATE,
            entity_type="program",
            entity_id=program_id,
            before_state=before_state,
            after_state=after_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "program_id": str(program_id),
            "updates": data,
            "action": "update"
        }
        
        self._publish_outbox_event(
            event_type="program_updated",
            aggregate_type="program",
            aggregate_id=program_id,
            event_data=outbox_event_data
        )
        
        await self.program_repo.commit()
        await self.program_repo.refresh(existing)
        return existing

    async def delete_program(
        self,
        program_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> bool:
        """Delete a program."""
        program = await self.program_repo.get_by_id(MasjidProgram, program_id)
        if not program:
            return False
        
        # Store before state
        before_state = {
            field: getattr(program, field)
            for field in program.__table__.columns.keys()
            if hasattr(program, field)
        }
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="program_editor",
            action=AuditAction.DELETE,
            entity_type="program",
            entity_id=program_id,
            before_state=before_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "program_id": str(program_id),
            "action": "delete"
        }
        
        self._publish_outbox_event(
            event_type="program_deleted",
            aggregate_type="program",
            aggregate_id=program_id,
            event_data=outbox_event_data
        )
        
        # Delete the program
        await self.program_repo.delete(MasjidProgram, program_id)
        await self.program_repo.commit()
        return True

    async def get_program(self, program_id: uuid.UUID) -> Optional[MasjidProgram]:
        """Get a program by ID."""
        return await self.program_repo.get_by_id(MasjidProgram, program_id)

    async def get_programs_by_masjid(
        self,
        masjid_id: uuid.UUID,
        program_type: str = None,
        is_active: bool = None
    ) -> List[MasjidProgram]:
        """Get programs for a masjid with optional filters."""
        return await self.program_repo.get_by_masjid(
            masjid_id, program_type=program_type, is_active=is_active
        )

    async def get_programs_by_type(
        self,
        program_type: str,
        masjid_id: uuid.UUID = None
    ) -> List[MasjidProgram]:
        """Get programs by type, optionally filtered by masjid."""
        return await self.program_repo.get_by_type(program_type, masjid_id)


class PhotoService(BaseService):
    """Service for MasjidPhoto business logic."""

    async def upload_photo(
        self,
        masjid_id: uuid.UUID,
        file_data: Dict,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> MasjidPhoto:
        """Upload a new photo."""
        # Validate required fields
        required_fields = ["filename", "file_path", "mime_type", "size"]
        for field in required_fields:
            if field not in file_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate file type
        from app.config import settings
        if file_data["mime_type"] not in settings.ALLOWED_PHOTO_MIME_TYPES:
            raise ValueError(f"Invalid photo type. Allowed types: {', '.join(settings.ALLOWED_PHOTO_MIME_TYPES)}")
        
        # Validate file size
        if file_data["size"] > settings.max_upload_size_bytes:
            raise ValueError(f"File size exceeds {settings.max_upload_size_bytes // (1024*1024)} MB limit")
        
        # Set masjid_id
        file_data["masjid_id"] = masjid_id
        file_data["moderation_status"] = PhotoModerationStatus.PENDING
        
        # Create photo record
        photo = await self.photo_repo.create(MasjidPhoto, file_data)
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="photo_editor",
            action=AuditAction.UPLOAD_PHOTO,
            entity_type="photo",
            entity_id=photo.id,
            after_state=file_data,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "photo_id": str(photo.id),
            "filename": file_data["filename"],
            "size": file_data["size"],
            "action": "create"
        }
        
        self._publish_outbox_event(
            event_type="photo_uploaded",
            aggregate_type="photo",
            aggregate_id=photo.id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        await self.photo_repo.commit()
        return photo

    async def delete_photo(
        self,
        photo_id: uuid.UUID,
        masjid_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: str = None
    ) -> bool:
        """Delete a photo."""
        # Get photo first to validate ownership
        photo = await self.photo_repo.get_by_id(MasjidPhoto, photo_id)
        if not photo:
            return False
        
        if photo.masjid_id != masjid_id:
            raise ValueError("You can only delete photos from your own masjid")
        
        # Store before state
        before_state = {
            field: getattr(photo, field)
            for field in photo.__table__.columns.keys()
            if hasattr(photo, field)
        }
        
        # Create audit event
        audit_event = self._create_audit_event(
            actor_id=user_id,
            actor_type="photo_editor",
            action=AuditAction.DELETE_PHOTO,
            entity_type="photo",
            entity_id=photo_id,
            before_state=before_state,
            request_id=request_id
        )
        self.session.add(audit_event)
        
        # Create outbox event
        outbox_event_data = {
            "masjid_id": str(masjid_id),
            "photo_id": str(photo_id),
            "action": "delete"
        }
        
        self._publish_outbox_event(
            event_type="photo_deleted",
            aggregate_type="photo",
            aggregate_id=photo_id,
            event_data=outbox_event_data,
            masjid_id=masjid_id
        )
        
        # Delete the photo
        await self.photo_repo.delete(MasjidPhoto, photo_id)
        await self.photo_repo.commit()
        return True

    async def get_photo(self, photo_id: uuid.UUID) -> Optional[MasjidPhoto]:
        """Get a photo by ID."""
        return await self.photo_repo.get_by_id(MasjidPhoto, photo_id)

    async def get_photos_by_masjid(
        self,
        masjid_id: uuid.UUID,
        moderation_status: str = None,
        is_featured: bool = None
    ) -> List[MasjidPhoto]:
        """Get photos for a masjid with optional filters."""
        return await self.photo_repo.get_by_masjid(
            masjid_id, moderation_status=moderation_status, is_featured=is_featured
        )


class SyncService(BaseService):
    """Service for sync and offline support operations."""

    _processed_mutation_ids: Set[str] = set()

    async def get_snapshot(
        self,
        cursor: str = None,
        entity_types: List[str] = None
    ) -> Dict[str, Any]:
        """Get a snapshot or delta of data."""
        snapshot = {
            "masjids": [],
            "salat_schedules": [],
            "programs": [],
            "people": [],
            "photos": []
        }
        
        # Get all data based on entity types
        if not entity_types or "masjids" in entity_types:
            snapshot["masjids"] = [
                self._masjid_to_dict(masjid)
                for masjid in await self.masjid_repo.get_all(Masjid)
            ]
        
        if not entity_types or "salat_schedules" in entity_types:
            snapshot["salat_schedules"] = [
                self._salat_schedule_to_dict(schedule)
                for schedule in await self.salat_repo.get_all(SalatSchedule)
            ]
        
        if not entity_types or "programs" in entity_types:
            snapshot["programs"] = [
                self._program_to_dict(program)
                for program in await self.program_repo.get_all(MasjidProgram)
            ]
        
        if not entity_types or "people" in entity_types:
            snapshot["people"] = [
                self._person_to_dict(person)
                for person in await self.person_repo.get_all(MasjidPerson)
            ]
        
        if not entity_types or "photos" in entity_types:
            snapshot["photos"] = [
                self._photo_to_dict(photo)
                for photo in await self.photo_repo.get_all(MasjidPhoto)
            ]
        
        return {
            "snapshot": snapshot,
            "cursor": str(datetime.utcnow().timestamp()),
            "has_more": False
        }

    async def process_mutations(
        self,
        mutations: List[Dict]
    ) -> List[Dict]:
        """Process queued mutations and return results with idempotency."""
        results = []
        
        for mutation in mutations:
            mut_id = mutation.get("id")
            if mut_id and mut_id in self._processed_mutation_ids:
                results.append({
                    "id": mut_id,
                    "status": "duplicate",
                    "result": None
                })
                continue

            try:
                result = await self._process_single_mutation(mutation)
                if mut_id:
                    self._processed_mutation_ids.add(mut_id)
                results.append({
                    "id": mut_id,
                    "status": "processed",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "id": mut_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        await self.masjid_repo.commit()
        return results

    async def _process_single_mutation(self, mutation: Dict) -> Any:
        """Process a single mutation based on its type and entity."""
        raw_type = (mutation.get("type") or "").upper()
        entity = (mutation.get("entity") or "").lower()
        payload = mutation.get("payload") if "payload" in mutation else mutation.get("data", {})
        if not isinstance(payload, dict):
            payload = {}
        payload = {k: v for k, v in payload.items() if not k.startswith("_")}
        
        # Support legacy snake_case type like "masjid_create"
        if "_" in (mutation.get("type") or ""):
            parts = mutation["type"].lower().split("_", 1)
            if not entity:
                entity = parts[0]
            raw_type = parts[1].upper()
        
        entity_id = payload.get("id") or mutation.get("id")

        if entity == "masjid":
            if raw_type == "CREATE":
                return await self.masjid_repo.create(Masjid, payload)
            elif raw_type == "UPDATE":
                return await self.masjid_repo.update(Masjid, uuid.UUID(str(entity_id)), payload)
            elif raw_type == "DELETE":
                return await self.masjid_repo.delete(Masjid, uuid.UUID(str(entity_id)))
            else:
                raise ValueError(f"Unknown mutation type {raw_type} for entity {entity}")
                
        elif entity in ("salat_schedule", "salat"):
            if raw_type == "CREATE":
                return await self.salat_repo.create(SalatSchedule, payload)
            elif raw_type == "UPDATE":
                return await self.salat_repo.update(SalatSchedule, uuid.UUID(str(entity_id)), payload)
            elif raw_type == "DELETE":
                return await self.salat_repo.delete(SalatSchedule, uuid.UUID(str(entity_id)))
            else:
                raise ValueError(f"Unknown mutation type {raw_type} for entity {entity}")

        elif entity == "program":
            if raw_type == "CREATE":
                return await self.program_repo.create(MasjidProgram, payload)
            elif raw_type == "UPDATE":
                return await self.program_repo.update(MasjidProgram, uuid.UUID(str(entity_id)), payload)
            elif raw_type == "DELETE":
                return await self.program_repo.delete(MasjidProgram, uuid.UUID(str(entity_id)))
            else:
                raise ValueError(f"Unknown mutation type {raw_type} for entity {entity}")

        elif entity == "person":
            if raw_type == "CREATE":
                return await self.person_repo.create(MasjidPerson, payload)
            elif raw_type == "UPDATE":
                return await self.person_repo.update(MasjidPerson, uuid.UUID(str(entity_id)), payload)
            elif raw_type == "DELETE":
                return await self.person_repo.delete(MasjidPerson, uuid.UUID(str(entity_id)))
            else:
                raise ValueError(f"Unknown mutation type {raw_type} for entity {entity}")
        else:
            raise ValueError(f"Unknown entity or mutation: entity={entity}, type={raw_type}")

    def _masjid_to_dict(self, masjid: Masjid) -> Dict[str, Any]:
        """Convert a Masjid model to a dictionary."""
        return {
            "id": str(masjid.id),
            "name": masjid.name,
            "address_line1": masjid.address_line1,
            "address_line2": masjid.address_line2,
            "city": masjid.city,
            "state": masjid.state,
            "postal_code": masjid.postal_code,
            "country": masjid.country,
            "latitude": masjid.latitude,
            "longitude": masjid.longitude,
            "timezone": masjid.timezone,
            "map_id": masjid.map_id,
            "accessible_by_public_transport": masjid.accessible_by_public_transport,
            "accessibility_details": masjid.accessibility_details,
            "highway_masjid": masjid.highway_masjid,
            "on_road_masjid": masjid.on_road_masjid,
            "opens_at": str(masjid.opens_at) if masjid.opens_at else None,
            "closes_at": str(masjid.closes_at) if masjid.closes_at else None,
            "is_24_hours": masjid.is_24_hours,
            "ramadan_adjusted_hours": masjid.ramadan_adjusted_hours,
            "has_wudu_stations": masjid.has_wudu_stations,
            "has_urinals": masjid.has_urinals,
            "has_toilets": masjid.has_toilets,
            "has_womens_prayer_area": masjid.has_womens_prayer_area,
            "has_library": masjid.has_library,
            "has_parking": masjid.has_parking,
            "has_street_parking": masjid.has_street_parking,
            "other_items": masjid.other_items,
            "meta": masjid.meta,
            "created_at": masjid.created_at.isoformat() if masjid.created_at else None,
            "updated_at": masjid.updated_at.isoformat() if masjid.updated_at else None,
        }

    def _salat_schedule_to_dict(self, schedule: SalatSchedule) -> Dict[str, Any]:
        """Convert a SalatSchedule model to a dictionary."""
        return {
            "id": str(schedule.id),
            "masjid_id": str(schedule.masjid_id),
            "salat_name": schedule.salat_name,
            "adhan_time": str(schedule.adhan_time) if schedule.adhan_time else None,
            "iqama_time": str(schedule.iqama_time) if schedule.iqama_time else None,
            "khutbah_time": str(schedule.khutbah_time) if schedule.khutbah_time else None,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
            "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
        }

    def _program_to_dict(self, program: MasjidProgram) -> Dict[str, Any]:
        """Convert a MasjidProgram model to a dictionary."""
        return {
            "id": str(program.id),
            "masjid_id": str(program.masjid_id),
            "type": program.type,
            "name": program.name,
            "description": program.description,
            "max_participants": program.max_participants,
            "is_active": program.is_active,
            "created_at": program.created_at.isoformat() if program.created_at else None,
            "updated_at": program.updated_at.isoformat() if program.updated_at else None,
        }

    def _person_to_dict(self, person: MasjidPerson) -> Dict[str, Any]:
        """Convert a MasjidPerson model to a dictionary."""
        return {
            "id": str(person.id),
            "masjid_id": str(person.masjid_id),
            "full_name": person.full_name,
            "role": person.role,
            "access_level": person.access_level,
            "phone_primary": person.phone_primary,
            "phone_alternate": person.phone_alternate,
            "email": person.email,
            "skills": person.skills,
            "bio": person.bio,
            "photo_url": person.photo_url,
            "is_active": person.is_active,
            "created_at": person.created_at.isoformat() if person.created_at else None,
            "updated_at": person.updated_at.isoformat() if person.updated_at else None,
        }

    def _photo_to_dict(self, photo: MasjidPhoto) -> Dict[str, Any]:
        """Convert a MasjidPhoto model to a dictionary."""
        return {
            "id": str(photo.id),
            "masjid_id": str(photo.masjid_id),
            "filename": photo.filename,
            "file_path": photo.file_path,
            "mime_type": photo.mime_type,
            "size": photo.size,
            "width": photo.width,
            "height": photo.height,
            "caption": photo.caption,
            "order_index": photo.order_index,
            "is_featured": photo.is_featured,
            "moderation_status": photo.moderation_status,
            "reviewer_id": str(photo.reviewer_id) if photo.reviewer_id else None,
            "review_reason": photo.review_reason,
            "reviewed_at": photo.reviewed_at.isoformat() if photo.reviewed_at else None,
            "created_at": photo.created_at.isoformat() if photo.created_at else None,
            "updated_at": photo.updated_at.isoformat() if photo.updated_at else None,
        }


# Service factory functions (create fresh service per request)

def get_masjid_service(session: AsyncSession) -> MasjidService:
    """Get a masjid service instance."""
    return MasjidService(session)


def get_salat_service(session: AsyncSession) -> SalatScheduleService:
    """Get the salat schedule service instance."""
    return SalatScheduleService(session)


def get_person_service(session: AsyncSession) -> PersonService:
    """Get the person service instance."""
    return PersonService(session)


def get_program_service(session: AsyncSession) -> ProgramService:
    """Get the program service instance."""
    return ProgramService(session)


def get_photo_service(session: AsyncSession) -> PhotoService:
    """Get the photo service instance."""
    return PhotoService(session)


def get_sync_service(session: AsyncSession) -> SyncService:
    """Get the sync service instance."""
    return SyncService(session)
