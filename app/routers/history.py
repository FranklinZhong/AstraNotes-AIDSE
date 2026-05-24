"""Version history router — GET versions and POST revert endpoints. Sprint 8."""
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.schemas.history import VersionEntryResponse, VersionHistoryResponse
from app.schemas.note import NoteResponse
from app.service_deps import get_note_service
from AstraNotes_v1.services.note_service import NoteService
from AstraNotes_v1.exceptions import NoteNotFoundError, AccessDeniedError

router = APIRouter()


@router.get("/{note_id}/versions", response_model=VersionHistoryResponse)
def get_note_versions(
    note_id: str,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """List all version snapshots for a note. (FR-06)"""
    try:
        service.get_note(user_id=user_id, note_id=note_id)
    except NoteNotFoundError:
        raise HTTPException(status_code=404, detail=f"Note {note_id!r} not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")

    raw = service.repository.get_versions(note_id)
    versions = [
        VersionEntryResponse(
            note_id=v["note_id"],
            version=v["version"],
            change_type=v["change_type"],
            at=v["at"],
            actor_id=v.get("actor_id"),
            title=v["data"].get("title", ""),
        )
        for v in raw
    ]
    return VersionHistoryResponse(note_id=note_id, versions=versions, total=len(versions))


@router.post("/{note_id}/revert/{version}", response_model=NoteResponse)
def revert_note_to_version(
    note_id: str,
    version: int,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Revert a note to a previous version snapshot. (FR-06)"""
    try:
        reverted = service.revert_note(user_id=user_id, note_id=note_id, version=version)
        return NoteResponse.from_domain(reverted)
    except NoteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")
