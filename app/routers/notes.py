"""Notes router — CRUD endpoints for /notes."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import List, Optional

from app.auth.dependencies import get_current_user
from app.schemas.note import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate
from app.service_deps import get_note_service
from AstraNotes_v1.services.note_service import NoteService
from AstraNotes_v1.exceptions import NoteNotFoundError, AccessDeniedError

router = APIRouter()


@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(
    body: NoteCreate,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Create a new note. (FR-01, US-01)"""
    note = service.create_note(
        author_id=user_id,
        title=body.title,
        body=body.body,
        tags=body.tags,
        visibility=body.visibility,
    )
    return NoteResponse.from_domain(note)


@router.get("/", response_model=NoteListResponse)
def list_notes(
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
    tags: Optional[List[str]] = Query(default=None, description="Filter by tags (any match)"),
):
    """List notes visible to the current user, optionally filtered by tags. (FR-03, US-03)"""
    notes = service.list_notes(user_id=user_id)
    if tags:
        tag_set = set(tags)
        notes = [n for n in notes if tag_set.intersection(getattr(n, "tags", []))]
    return NoteListResponse(notes=[NoteResponse.from_domain(n) for n in notes], total=len(notes))


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: str,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Get a single note by ID. (FR-01, US-01)"""
    try:
        note = service.get_note(user_id=user_id, note_id=note_id)
        return NoteResponse.from_domain(note)
    except NoteNotFoundError:
        raise HTTPException(status_code=404, detail=f"Note {note_id!r} not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    body: NoteUpdate,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Update note fields. (FR-02, US-02)"""
    try:
        note = service.update_note(
            user_id=user_id,
            note_id=note_id,
            title=body.title,
            body=body.body,
            visibility=body.visibility,
        )
        return NoteResponse.from_domain(note)
    except NoteNotFoundError:
        raise HTTPException(status_code=404, detail=f"Note {note_id!r} not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: str,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Delete a note by ID. (FR-03, US-03)"""
    try:
        service.delete_note(user_id=user_id, note_id=note_id)
    except NoteNotFoundError:
        raise HTTPException(status_code=404, detail=f"Note {note_id!r} not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")
