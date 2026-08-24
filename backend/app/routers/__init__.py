"""Routers for the Jumapp API.

This module contains all FastAPI routers for the Jumapp API,
implementing CRUD endpoints for all entities with proper validation,
authorization, and error handling.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Path, Query, Request, status
from fastapi.responses import JSONResponse

from app.auth import get_current_user_dependency, User
from app.services import (
    get_masjid_service, get_salat_service, get_person_service,
    get_program_service, get_photo_service, get_sync_service
)
from app.enums import (
    SalatName, AccessLevel, PersonRole, ProgramType, 
    ScheduleFrequency, PhotoModerationStatus
)
from app.schemas import (
    MasjidCreate, MasjidUpdate, MasjidResponse,
    SalatScheduleCreate, SalatScheduleUpdate, SalatScheduleResponse,
    ProgramCreate, ProgramUpdate, ProgramResponse,
    PersonCreate, PersonUpdate, PersonResponse,
    PhotoUpload, PhotoResponse,
    SyncMutationsRequest,
    RoleRequestUpdate,
    DeleteResponse,
)

# Masjids Router
masjid_router = APIRouter(prefix="/masjids", tags=["Masjids"])


@masjid_router.get("/")
async def list_masjids(
    request: Request,
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    radius: Optional[int] = Query(2000, description="Search radius in meters"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State name"),
    accessible_by_transport: Optional[bool] = Query(None, description="Accessibility by public transport"),
    current_user: User = Depends(get_current_user_dependency)
) -> List[dict]:
    """List masjids with optional filters."""
    try:
        if not current_user.has_permission("masjid:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view masjids"
            )

        masjid_service = get_masjid_service(request.state.db)
        masjids = await masjid_service.list_masjids(
            lat=lat,
            lon=lon,
            radius=radius,
            city=city,
            state=state,
            accessible_by_transport=accessible_by_transport,
            include_related=True
        )
        
        return [
            {
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
                "salat_schedules": [
                    {
                        "id": str(schedule.id),
                        "salat_name": schedule.salat_name,
                        "adhan_time": str(schedule.adhan_time) if schedule.adhan_time else None,
                        "iqama_time": str(schedule.iqama_time) if schedule.iqama_time else None,
                        "khutbah_time": str(schedule.khutbah_time) if schedule.khutbah_time else None,
                    }
                    for schedule in masjid.schedules
                ],
                "programs": [
                    {
                        "id": str(program.id),
                        "type": program.type,
                        "name": program.name,
                        "description": program.description,
                        "max_participants": program.max_participants,
                        "is_active": program.is_active,
                    }
                    for program in masjid.programs
                ],
                "people": [
                    {
                        "id": str(person.id),
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
                    }
                    for person in masjid.people
                ],
                "photos": [
                    {
                        "id": str(photo.id),
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
                        "review_reason": photo.review_reason,
                    }
                    for photo in masjid.photos
                ],
            }
            for masjid in masjids
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@masjid_router.get("/{masjid_id}")
async def get_masjid(
    request: Request,
    masjid_id: UUID = Path(..., description="Masjid ID"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Get a masjid by ID."""
    try:
        if not current_user.has_permission("masjid:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view masjids"
            )

        masjid_service = get_masjid_service(request.state.db)
        masjid = await masjid_service.get_masjid(masjid_id, include_related=True)
        
        if not masjid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Masjid with ID {masjid_id} not found"
            )
        
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
            "salat_schedules": [
                {
                    "id": str(schedule.id),
                    "salat_name": schedule.salat_name,
                    "adhan_time": str(schedule.adhan_time) if schedule.adhan_time else None,
                    "iqama_time": str(schedule.iqama_time) if schedule.iqama_time else None,
                    "khutbah_time": str(schedule.khutbah_time) if schedule.khutbah_time else None,
                }
                for schedule in masjid.schedules
            ],
            "programs": [
                {
                    "id": str(program.id),
                    "type": program.type,
                    "name": program.name,
                    "description": program.description,
                    "max_participants": program.max_participants,
                    "is_active": program.is_active,
                }
                for program in masjid.programs
            ],
            "people": [
                {
                    "id": str(person.id),
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
                }
                for person in masjid.people
            ],
            "photos": [
                {
                    "id": str(photo.id),
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
                    "review_reason": photo.review_reason,
                }
                for photo in masjid.photos
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@masjid_router.post("/", response_model=MasjidResponse)
async def create_masjid(
    request: Request,
    data: MasjidCreate,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Create a new masjid."""
    try:
        # Check permission
        if not current_user.has_permission("masjid:create"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create masjids"
            )
        
        masjid_dict = data.model_dump()
        masjid_service = get_masjid_service(request.state.db)
        masjid = await masjid_service.create_masjid(
            data=masjid_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
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
            "created_at": masjid.created_at.isoformat() if masjid.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@masjid_router.patch("/{masjid_id}", response_model=MasjidResponse)
async def update_masjid(
    request: Request,
    masjid_id: UUID = Path(..., description="Masjid ID"),
    data: MasjidUpdate = Body(...),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Update an existing masjid."""
    try:
        # Check permission
        if not current_user.has_permission("masjid:update", str(masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this masjid"
            )
        
        update_dict = data.model_dump(exclude_unset=True)
        masjid_service = get_masjid_service(request.state.db)
        masjid = await masjid_service.update_masjid(
            masjid_id=masjid_id,
            data=update_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        if not masjid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Masjid with ID {masjid_id} not found"
            )
        
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
            "updated_at": masjid.updated_at.isoformat() if masjid.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@masjid_router.delete("/{masjid_id}", response_model=DeleteResponse)
async def delete_masjid(
    request: Request,
    masjid_id: UUID = Path(..., description="Masjid ID"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Delete a masjid."""
    try:
        # Check permission
        if not current_user.has_permission("masjid:delete", str(masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this masjid"
            )
        
        masjid_service = get_masjid_service(request.state.db)
        success = await masjid_service.delete_masjid(
            masjid_id=masjid_id,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Masjid with ID {masjid_id} not found"
            )
        
        return {"id": str(masjid_id), "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Salat Schedules Router
salat_router = APIRouter(prefix="/schedules", tags=["Salat Schedules"])


@salat_router.get("/")
async def list_schedules(
    request: Request,
    masjid_id: Optional[UUID] = Query(None, description="Masjid ID"),
    salat_name: Optional[SalatName] = Query(None, description="Salat name"),
    current_user: User = Depends(get_current_user_dependency)
) -> List[dict]:
    """List salat schedules."""
    try:
        if not current_user.has_permission("salat:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view salat schedules"
            )

        salat_service = get_salat_service(request.state.db)
        
        if masjid_id:
            schedules = await salat_service.get_by_masjid(masjid_id)
        elif salat_name:
            # Note: This would need to filter by masjid_id as well in the service
            schedules = await salat_service.get_all_by_filters(salat_name=salat_name)
        else:
            schedules = await salat_service.get_all()
        
        return [
            {
                "id": str(schedule.id),
                "masjid_id": str(schedule.masjid_id),
                "salat_name": schedule.salat_name,
                "adhan_time": str(schedule.adhan_time) if schedule.adhan_time else None,
                "iqama_time": str(schedule.iqama_time) if schedule.iqama_time else None,
                "khutbah_time": str(schedule.khutbah_time) if schedule.khutbah_time else None,
                "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
                "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
            }
            for schedule in schedules
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@salat_router.get("/{schedule_id}")
async def get_schedule(
    schedule_id: UUID = Path(..., description="Schedule ID"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Get a salat schedule by ID."""
    try:
        if not current_user.has_permission("salat:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view salat schedules"
            )

        salat_service = get_salat_service(current_user.db)
        schedule = await salat_service.get_schedule(schedule_id)
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Salat schedule with ID {schedule_id} not found"
            )
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@salat_router.post("/")
async def create_schedule(
    request: Request,
    data: SalatScheduleCreate,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Create a new salat schedule."""
    try:
        # Check permission
        if not current_user.has_permission("salat:create", str(data.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create salat schedules for this masjid"
            )
        
        schedule_dict = data.model_dump()
        schedule_dict["masjid_id"] = str(data.masjid_id)
        if isinstance(schedule_dict.get("salat_name"), SalatName):
            schedule_dict["salat_name"] = data.salat_name.value
        
        salat_service = get_salat_service(request.state.db)
        schedule = await salat_service.create_schedule(
            masjid_id=data.masjid_id,
            data=schedule_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        return {
            "id": str(schedule.id),
            "masjid_id": str(schedule.masjid_id),
            "salat_name": schedule.salat_name,
            "adhan_time": str(schedule.adhan_time) if schedule.adhan_time else None,
            "iqama_time": str(schedule.iqama_time) if schedule.iqama_time else None,
            "khutbah_time": str(schedule.khutbah_time) if schedule.khutbah_time else None,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@salat_router.patch("/{schedule_id}")
async def update_schedule(
    request: Request,
    schedule_id: UUID = Path(..., description="Schedule ID"),
    data: SalatScheduleUpdate = Body(...),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Update an existing salat schedule."""
    try:
        salat_service = get_salat_service(request.state.db)
        existing_schedule = await salat_service.get_schedule(schedule_id)
        if not existing_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Salat schedule with ID {schedule_id} not found"
            )

        # Check permission for updating salat times
        if not current_user.has_permission("salat:update", str(existing_schedule.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update salat schedules for this masjid"
            )
        
        update_dict = data.model_dump(exclude_unset=True)
        schedule = await salat_service.update_schedule(
            schedule_id=schedule_id,
            data=update_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        return {
            "id": str(schedule.id),
            "masjid_id": str(schedule.masjid_id),
            "salat_name": schedule.salat_name,
            "adhan_time": str(schedule.adhan_time) if schedule.adhan_time else None,
            "iqama_time": str(schedule.iqama_time) if schedule.iqama_time else None,
            "khutbah_time": str(schedule.khutbah_time) if schedule.khutbah_time else None,
            "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@salat_router.delete("/{schedule_id}")
async def delete_schedule(
    request: Request,
    schedule_id: UUID = Path(..., description="Schedule ID"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Delete a salat schedule."""
    try:
        salat_service = get_salat_service(request.state.db)
        existing_schedule = await salat_service.get_schedule(schedule_id)
        if not existing_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Salat schedule with ID {schedule_id} not found"
            )

        # Check permission
        if not current_user.has_permission("salat:delete", str(existing_schedule.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete salat schedules for this masjid"
            )
        
        success = await salat_service.delete_schedule(
            schedule_id=schedule_id,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Salat schedule with ID {schedule_id} not found"
            )
        
        return {"id": str(schedule_id), "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Programs Router
program_router = APIRouter(prefix="/programs", tags=["Programs"])


@program_router.get("/")
async def list_programs(
    request: Request,
    masjid_id: Optional[UUID] = Query(None, description="Masjid ID"),
    program_type: Optional[ProgramType] = Query(None, description="Program type"),
    current_user: User = Depends(get_current_user_dependency)
) -> List[dict]:
    """List programs."""
    try:
        if not current_user.has_permission("program:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view programs"
            )

        program_service = get_program_service(request.state.db)
        
        if masjid_id:
            programs = await program_service.get_programs_by_masjid(masjid_id, program_type)
        elif program_type:
            programs = await program_service.get_programs_by_type(program_type)
        else:
            programs = await program_service.get_all()
        
        return [
            {
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
            for program in programs
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@program_router.get("/{program_id}")
async def get_program(
    program_id: UUID = Path(..., description="Program ID"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Get a program by ID."""
    try:
        if not current_user.has_permission("program:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view programs"
            )

        program_service = get_program_service(current_user.db)
        program = await program_service.get_program(program_id)
        
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@program_router.post("/")
async def create_program(
    request: Request,
    data: ProgramCreate,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Create a new program."""
    try:
        # Check permission
        if not current_user.has_permission("program:create", str(data.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create programs for this masjid"
            )
        
        program_dict = data.model_dump()
        program_dict["masjid_id"] = str(data.masjid_id)
        if isinstance(program_dict.get("type"), ProgramType):
            program_dict["type"] = data.type.value
        
        program_service = get_program_service(request.state.db)
        program = await program_service.create_program(
            masjid_id=data.masjid_id,
            data=program_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        return {
            "id": str(program.id),
            "masjid_id": str(program.masjid_id),
            "type": program.type,
            "name": program.name,
            "description": program.description,
            "max_participants": program.max_participants,
            "is_active": program.is_active,
            "created_at": program.created_at.isoformat() if program.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@program_router.patch("/{program_id}")
async def update_program(
    request: Request,
    program_id: UUID = Path(..., description="Program ID"),
    data: ProgramUpdate = Body(...),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Update an existing program."""
    try:
        program_service = get_program_service(request.state.db)
        existing_program = await program_service.get_program(program_id)
        if not existing_program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )

        # Check permission
        if not current_user.has_permission("program:update", str(existing_program.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update programs for this masjid"
            )
        
        update_dict = data.model_dump(exclude_unset=True)
        program = await program_service.update_program(
            program_id=program_id,
            data=update_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        return {
            "id": str(program.id),
            "masjid_id": str(program.masjid_id),
            "type": program.type,
            "name": program.name,
            "description": program.description,
            "max_participants": program.max_participants,
            "is_active": program.is_active,
            "updated_at": program.updated_at.isoformat() if program.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@program_router.delete("/{program_id}")
async def delete_program(
    request: Request,
    program_id: UUID = Path(..., description="Program ID"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Delete a program."""
    try:
        program_service = get_program_service(request.state.db)
        existing_program = await program_service.get_program(program_id)
        if not existing_program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )

        # Check permission
        if not current_user.has_permission("program:delete", str(existing_program.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete programs for this masjid"
            )
        
        success = await program_service.delete_program(
            program_id=program_id,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
        
        return {"id": str(program_id), "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# People Router
person_router = APIRouter(prefix="/people", tags=["People"])


@person_router.get("/")
async def list_people(
    request: Request,
    masjid_id: Optional[UUID] = Query(None, description="Masjid ID"),
    role: Optional[PersonRole] = Query(None, description="Role"),
    access_level: Optional[AccessLevel] = Query(None, description="Access level"),
    is_active: Optional[bool] = Query(None, description="Active status"),
    current_user: User = Depends(get_current_user_dependency)
) -> List[dict]:
    """List people."""
    try:
        if not current_user.has_permission("person:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view people"
            )

        person_service = get_person_service(request.state.db)
        
        if masjid_id:
            people = await person_service.get_persons_by_masjid(
                masjid_id, role, access_level, is_active
            )
        else:
            people = await person_service.get_all()
        
        return [
            {
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
            for person in people
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@person_router.get("/{person_id}")
async def get_person(
    person_id: UUID = Path(..., description="Person ID"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Get a person by ID."""
    try:
        if not current_user.has_permission("person:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view people"
            )

        person_service = get_person_service(current_user.db)
        person = await person_service.get_person(person_id)
        
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with ID {person_id} not found"
            )
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@person_router.post("/")
async def create_person(
    request: Request,
    data: PersonCreate,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Create a new person."""
    try:
        # Check permission
        if not current_user.has_permission("person:create", str(data.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create people for this masjid"
            )
        
        person_dict = data.model_dump()
        person_dict["masjid_id"] = str(data.masjid_id)
        if isinstance(person_dict.get("role"), PersonRole):
            person_dict["role"] = data.role.value
        if isinstance(person_dict.get("access_level"), AccessLevel):
            person_dict["access_level"] = data.access_level.value

        person_service = get_person_service(request.state.db)
        person = await person_service.create_person(
            masjid_id=data.masjid_id,
            data=person_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
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
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@person_router.patch("/{person_id}")
async def update_person(
    request: Request,
    person_id: UUID = Path(..., description="Person ID"),
    data: PersonUpdate = Body(...),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Update an existing person."""
    try:
        person_service = get_person_service(request.state.db)
        existing_person = await person_service.get_person(person_id)
        if not existing_person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with ID {person_id} not found"
            )

        # Check permission
        if not current_user.has_permission("person:update", str(existing_person.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update people for this masjid"
            )
        
        update_dict = data.model_dump(exclude_unset=True)
        person = await person_service.update_person(
            person_id=person_id,
            data=update_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
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
            "updated_at": person.updated_at.isoformat() if person.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@person_router.delete("/{person_id}")
async def delete_person(
    request: Request,
    person_id: UUID = Path(..., description="Person ID"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Delete a person."""
    try:
        person_service = get_person_service(request.state.db)
        existing_person = await person_service.get_person(person_id)
        if not existing_person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with ID {person_id} not found"
            )

        # Check permission
        if not current_user.has_permission("person:delete", str(existing_person.masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete people for this masjid"
            )
        
        success = await person_service.delete_person(
            person_id=person_id,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with ID {person_id} not found"
            )
        
        return {"id": str(person_id), "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Photos Router
photo_router = APIRouter(prefix="/photos", tags=["Photos"])


@photo_router.post("/masjids/{masjid_id}/photos")
async def upload_photo(
    request: Request,
    masjid_id: UUID = Path(..., description="Masjid ID"),
    data: PhotoUpload = Body(...),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Upload a photo to a masjid."""
    try:
        # Check permission
        if not current_user.has_permission("photo:create", str(masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to upload photos to this masjid"
            )
        
        photo_dict = data.model_dump()
        photo_service = get_photo_service(request.state.db)
        photo = await photo_service.upload_photo(
            masjid_id=masjid_id,
            file_data=photo_dict,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
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
            "review_reason": photo.review_reason,
            "created_at": photo.created_at.isoformat() if photo.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@photo_router.delete("/masjids/{masjid_id}/photos/{photo_id}")
async def delete_photo(
    request: Request,
    masjid_id: UUID = Path(..., description="Masjid ID"),
    photo_id: UUID = Path(..., description="Photo ID"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID", description="Request ID for audit tracing"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Delete a photo."""
    try:
        # Check permission
        if not current_user.has_permission("photo:delete", str(masjid_id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete photos from this masjid"
            )
        
        photo_service = get_photo_service(request.state.db)
        success = await photo_service.delete_photo(
            photo_id=photo_id,
            masjid_id=masjid_id,
            user_id=current_user.id,
            request_id=x_request_id or request.headers.get("X-Request-ID")
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Photo with ID {photo_id} not found"
            )
        
        return {"id": str(photo_id), "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Sync Router
sync_router = APIRouter(prefix="/sync", tags=["Sync"])


@sync_router.get("/")
async def get_sync_snapshot(
    request: Request,
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    entity_types: Optional[List[str]] = Query(None, description="Types of entities to sync"),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Get a sync snapshot or delta."""
    try:
        sync_service = get_sync_service(request.state.db)
        snapshot = await sync_service.get_snapshot(
            cursor=cursor,
            entity_types=entity_types
        )
        
        return snapshot
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@sync_router.post("/mutations")
async def sync_mutations(
    request: Request,
    data: SyncMutationsRequest,
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Sync mutations from client."""
    try:
        # Check permission
        if not current_user.has_permission("sync:write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to sync mutations"
            )
        
        sync_dict = data.model_dump()
        mutations = sync_dict.get("mutations", [])
        
        sync_service = get_sync_service(request.state.db)
        results = await sync_service.process_mutations(mutations)
        
        return {
            "processed": len([r for r in results if r["status"] == "processed"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Admin Router
admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get("/role-requests")
async def list_role_requests(
    current_user: User = Depends(get_current_user_dependency)
) -> List[dict]:
    """List role requests."""
    try:
        # Check permission
        if not current_user.has_permission("admin:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view role requests"
            )
        
        # Note: Role request functionality would need to be implemented
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@admin_router.patch("/role-requests/{role_request_id}")
async def update_role_request(
    request: Request,
    role_request_id: UUID = Path(..., description="Role Request ID"),
    data: RoleRequestUpdate = Body(...),
    current_user: User = Depends(get_current_user_dependency)
) -> dict:
    """Update a role request status."""
    try:
        # Check permission
        if not current_user.has_permission("admin:approve"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to approve role requests"
            )
        
        # Note: Role request update functionality would need to be implemented
        return {"id": str(role_request_id), "status": "updated"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@admin_router.get("/audit-events")
async def list_audit_events(
    current_user: User = Depends(get_current_user_dependency)
) -> List[dict]:
    """List audit events."""
    try:
        # Check permission
        if not current_user.has_permission("admin:read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view audit events"
            )
        
        # Note: Audit event listing functionality would need to be implemented
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Include all routers in the main FastAPI app
routers = [
    masjid_router,
    salat_router,
    program_router,
    person_router,
    photo_router,
    sync_router,
    admin_router,
]
