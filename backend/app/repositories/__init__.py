"""Repository layer for database operations.

This layer provides abstract database access through SQLAlchemy repositories,
enabling clean separation between business logic and data persistence.
"""

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.masjid import Masjid
from app.models.salat import SalatSchedule
from app.models.person import MasjidPerson
from app.models.program import MasjidProgram, ProgramSchedule
from app.models.photo import MasjidPhoto
from app.models.audit import AuditEvent
from app.models.outbox import OutboxEvent
from app.enums import SalatName, AccessLevel, PersonRole, ProgramType, ScheduleFrequency, PhotoModerationStatus


class BaseRepository:
    """Base repository with common database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, model, id: uuid.UUID, options: List = None) -> Optional[Any]:
        """Get an entity by its ID."""
        query = select(model).where(model.id == id)
        if options:
            for option in options:
                query = query.options(option)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, 
        model, 
        filters: Dict = None, 
        options: List = None,
        limit: int = None, 
        offset: int = None
    ) -> List[Any]:
        """Get all entities with optional filters."""
        query = select(model)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(model, key):
                    field = getattr(model, key)
                    if isinstance(value, list):
                        conditions.append(field.in_(value))
                    else:
                        conditions.append(field == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        if options:
            for option in options:
                query = query.options(option)
        
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, model, data: Dict) -> Any:
        """Create a new entity."""
        instance = model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, model, id: uuid.UUID, data: Dict) -> Optional[Any]:
        """Update an existing entity."""
        instance = await self.get_by_id(model, id)
        if not instance:
            return None
        
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await self.session.flush()
        return instance

    async def delete(self, model, id: uuid.UUID) -> bool:
        """Delete an entity."""
        instance = await self.get_by_id(model, id)
        if not instance:
            return False
        
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def refresh(self, instance):
        """Refresh an instance from the database."""
        await self.session.refresh(instance)


class MasjidRepository(BaseRepository):
    """Repository for Masjid operations."""

    async def get_by_location(
        self, 
        lat: float, 
        lon: float, 
        radius: int = 2000
    ) -> List[Masjid]:
        """Get masjids within a radius of the given coordinates."""
        # Using PostGIS function to calculate distance
        point = f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)"
        query = select(Masjid).where(
            func.ST_DWithin(
                Masjid.location,
                func.ST_GeomFromText(point),
                radius
            )
        ).order_by(
            func.ST_Distance(Masjid.location, func.ST_GeomFromText(point))
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_filters(
        self,
        lat: float = None,
        lon: float = None,
        radius: int = None,
        city: str = None,
        state: str = None,
        accessible_by_transport: bool = None,
        **kwargs
    ) -> List[Masjid]:
        """Get masjids with advanced filtering."""
        query = select(Masjid)
        
        # Build where conditions
        conditions = []
        
        if city:
            conditions.append(Masjid.city == city)
        
        if state:
            conditions.append(Masjid.state == state)
        
        if accessible_by_transport is not None:
            conditions.append(Masjid.accessible_by_public_transport == accessible_by_transport)
        
        if lat and lon and radius:
            point = f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)"
            conditions.append(
                func.ST_DWithin(Masjid.location, func.ST_GeomFromText(point), radius)
            )
        
        # Handle additional filters
        for key, value in kwargs.items():
            if hasattr(Masjid, key):
                field = getattr(Masjid, key)
                if isinstance(value, list):
                    conditions.append(field.in_(value))
                else:
                    conditions.append(field == value)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Join with related entities
        query = query.options(
            joinedload(Masjid.schedules),
            joinedload(Masjid.programs),
            joinedload(Masjid.people),
            joinedload(Masjid.photos)
        )
        
        result = await self.session.execute(query)
        return result.unique().scalars().all()


class SalatScheduleRepository(BaseRepository):
    """Repository for SalatSchedule operations."""

    async def get_by_masjid(self, masjid_id: uuid.UUID) -> List[SalatSchedule]:
        """Get all salat schedules for a masjid."""
        return await self.get_all(
            SalatSchedule,
            filters={"masjid_id": masjid_id}
        )

    async def get_by_salat_name(
        self, 
        masjid_id: uuid.UUID, 
        salat_name: str
    ) -> Optional[SalatSchedule]:
        """Get salat schedule by masjid and salat name."""
        return await self.get_by_id(
            SalatSchedule,
            uuid.UUID(salat_name)  # This should be masjid_id actually
        )


class PersonRepository(BaseRepository):
    """Repository for MasjidPerson operations."""

    async def get_by_masjid(
        self, 
        masjid_id: uuid.UUID,
        role: str = None,
        access_level: str = None,
        is_active: bool = None
    ) -> List[MasjidPerson]:
        """Get people for a masjid with optional filters."""
        filters = {"masjid_id": masjid_id}
        
        if role:
            filters["role"] = role
        
        if access_level:
            filters["access_level"] = access_level
        
        if is_active is not None:
            filters["is_active"] = is_active
        
        return await self.get_all(
            MasjidPerson,
            filters=filters
        )

    async def get_leaders(
        self,
        masjid_id: uuid.UUID,
        roles: List[str] = None
    ) -> List[MasjidPerson]:
        """Get masjid leaders (imams, muazzins, committee members)."""
        filters = {
            "masjid_id": masjid_id,
            "is_active": True
        }
        
        if roles:
            filters["role"] = roles
        
        return await self.get_all(
            MasjidPerson,
            filters=filters
        )


class ProgramRepository(BaseRepository):
    """Repository for MasjidProgram operations."""

    async def get_by_masjid(
        self,
        masjid_id: uuid.UUID,
        program_type: str = None,
        is_active: bool = None
    ) -> List[MasjidProgram]:
        """Get programs for a masjid with optional filters."""
        filters = {"masjid_id": masjid_id}
        
        if program_type:
            filters["type"] = program_type
        
        if is_active is not None:
            filters["is_active"] = is_active
        
        # Load schedules with this program
        return await self.get_all(
            MasjidProgram,
            filters=filters,
            options=[selectinload(MasjidProgram.schedules)]
        )

    async def get_by_type(
        self,
        program_type: str,
        masjid_id: uuid.UUID = None
    ) -> List[MasjidProgram]:
        """Get programs by type, optionally filtered by masjid."""
        filters = {"type": program_type}
        
        if masjid_id:
            filters["masjid_id"] = masjid_id
        
        return await self.get_all(MasjidProgram, filters=filters)


class PhotoRepository(BaseRepository):
    """Repository for MasjidPhoto operations."""

    async def get_by_masjid(
        self,
        masjid_id: uuid.UUID,
        moderation_status: str = None,
        is_featured: bool = None
    ) -> List[MasjidPhoto]:
        """Get photos for a masjid with optional filters."""
        filters = {"masjid_id": masjid_id}
        
        if moderation_status:
            filters["moderation_status"] = moderation_status
        
        if is_featured is not None:
            filters["is_featured"] = is_featured
        
        return await self.get_all(MasjidPhoto, filters=filters)

    async def get_approved_by_masjid(self, masjid_id: uuid.UUID) -> List[MasjidPhoto]:
        """Get approved photos for a masjid."""
        return await self.get_by_masjid(
            masjid_id,
            moderation_status=PhotoModerationStatus.APPROVED
        )


class AuditRepository(BaseRepository):
    """Repository for AuditEvent operations."""

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: uuid.UUID
    ) -> List[AuditEvent]:
        """Get audit events for a specific entity."""
        return await self.get_all(
            AuditEvent,
            filters={
                "entity_type": entity_type,
                "entity_id": entity_id
            },
            options=[joinedload(AuditEvent.actor)]
        )

    async def get_by_actor(
        self,
        actor_id: uuid.UUID,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Get audit events by actor."""
        return await self.get_all(
            AuditEvent,
            filters={"actor_id": actor_id},
            limit=limit
        )


class OutboxRepository(BaseRepository):
    """Repository for OutboxEvent operations."""

    async def get_pending_events(self) -> List[OutboxEvent]:
        """Get all pending outbox events for processing."""
        return await self.get_all(
            OutboxEvent,
            filters={"published": False}
        )

    async def mark_published(self, event_id: uuid.UUID) -> bool:
        """Mark an outbox event as published."""
        event = await self.get_by_id(OutboxEvent, event_id)
        if not event:
            return False
        
        event.published = True
        event.published_at = datetime.utcnow()
        await self.session.flush()
        return True

    async def increment_retry_count(self, event_id: uuid.UUID) -> bool:
        """Increment retry count for an event."""
        event = await self.get_by_id(OutboxEvent, event_id)
        if not event:
            return False
        
        event.retry_count += 1
        await self.session.flush()
        return True
