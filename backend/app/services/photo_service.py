"""Photo storage service for handling masjid photo uploads.

This service manages photo uploads to GCS or local storage, including validation,
resizing, and metadata management.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Tuple

from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


class PhotoStorageService:
    """Service for handling masjid photo storage operations."""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    async def upload_photo(
        self, 
        file: UploadFile, 
        masjid_id: str,
        uploaded_by: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload a photo to storage."""
        # Validate file
        self._validate_photo(file)

        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename

        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # If GCS configured, upload to GCS
        if settings.gcs_bucket:
            await self._upload_to_gcs(file_path, file.filename)

        return {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": str(file_path),
            "size": len(content),
            "mime_type": file.content_type,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

    async def delete_photo(self, photo_id: str, masjid_id: str) -> bool:
        """Delete a photo from storage."""
        # Implementation would include GCS cleanup if using GCS
        file_path = self.upload_dir / f"{photo_id}.jpg"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def get_photo_url(self, photo_id: str) -> str:
        """Get URL for accessing a photo."""
        if settings.gcs_bucket:
            return f"https://storage.googleapis.com/{settings.gcs_bucket}/{photo_id}"
        return f"{settings.upload_url_prefix}/{photo_id}"

    def _validate_photo(self, file: UploadFile) -> None:
        """Validate photo file upload."""
        # Check file type
        if file.content_type not in settings.ALLOWED_PHOTO_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid photo type. Allowed types: {', '.join(settings.ALLOWED_PHOTO_MIME_TYPES)}",
            )

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {settings.max_upload_size_bytes // (1024*1024)} MB limit",
            )

    async def _upload_to_gcs(self, file_path: Path, filename: str) -> None:
        """Upload file to Google Cloud Storage."""
        # This would require google-cloud-storage library
        # For now, just log the operation
        pass

    async def cleanup_orphaned_files(self) -> int:
        """Clean up orphaned files in storage."""
        # Implementation would clean up unused files
        return 0


# Global photo storage service instance
_photo_storage = PhotoStorageService()


def get_photo_storage_service() -> PhotoStorageService:
    """Get the photo storage service instance."""
    return _photo_storage
