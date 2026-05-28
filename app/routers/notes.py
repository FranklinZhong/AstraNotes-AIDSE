"""Notes router — CRUD endpoints for /notes."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from passlib.context import CryptContext
from typing import List, Optional

from app.auth.dependencies import get_current_user
from app.schemas.note import NoteCreate, EmergencyUnlockRequest, NoteListResponse, NoteResponse, NoteUpdate
from app.service_deps import get_note_service
from AstraNotes_v1.services.note_service import NoteService
from AstraNotes_v1.exceptions import NoteNotFoundError, AccessDeniedError, ValidationError

router = APIRouter()
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _require_note_password(note, provided: Optional[str]) -> None:
    """Raise HTTP 401/403 if a private note's password is missing or wrong.
    Private notes with no hash (e.g. after emergency unlock) are freely accessible.
    """
    if note.visibility != "private":
        return
    if not note.note_password_hash:
        return  # no hash set — accessible without password (user should set one)
    if not provided:
        raise HTTPException(status_code=401, detail="Note password required")
    if not _pwd_ctx.verify(provided, note.note_password_hash):
        raise HTTPException(status_code=403, detail="Incorrect note password")


@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(
    body: NoteCreate,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Create a new note. (FR-01, US-01)"""
    hash_ = _pwd_ctx.hash(body.note_password) if body.note_password else None
    note = service.create_note(
        author_id=user_id,
        title=body.title,
        body=body.body,
        tags=body.tags,
        visibility=body.visibility,
        note_password_hash=hash_,
    )
    return NoteResponse.from_domain(note)


@router.get("/", response_model=NoteListResponse)
def list_notes(
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
    tags: Optional[List[str]] = Query(default=None, description="Filter by tags (AND match)"),
):
    """List the current user's notes. Private note bodies are masked. (FR-03, US-03)"""
    notes = service.list_notes(user_id=user_id)
    if tags:
        tag_set = set(tags)
        notes = [n for n in notes if tag_set.issubset(getattr(n, "tags", []))]

    result = []
    for n in notes:
        resp = NoteResponse.from_domain(n)
        if n.visibility == "private":
            resp.body = ""  # mask body; full content requires X-Note-Password on GET /{id}
        result.append(resp)
    return NoteListResponse(notes=result, total=len(result))


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: str,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
    x_note_password: Optional[str] = Header(None, alias="X-Note-Password"),
):
    """Get a single note. Private notes require X-Note-Password header. (FR-01, US-01)"""
    try:
        note = service.get_note(user_id=user_id, note_id=note_id)
        _require_note_password(note, x_note_password)
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
    x_note_password: Optional[str] = Header(None, alias="X-Note-Password"),
):
    """Update note fields. Private notes require X-Note-Password header. (FR-02, US-02)"""
    try:
        # Fetch current note to verify ownership and note password.
        current = service.get_note(user_id=user_id, note_id=note_id)
        _require_note_password(current, x_note_password)

        # Determine new note_password_hash:
        #   - switching to public → clear hash
        #   - body.note_password provided → hash it (new or changed password)
        #   - staying private, no new password → keep existing hash
        new_visibility = body.visibility or current.visibility
        if new_visibility == "public":
            new_hash = None
        elif body.note_password:
            new_hash = _pwd_ctx.hash(body.note_password)
        else:
            new_hash = current.note_password_hash

        note = service.update_note(
            user_id=user_id,
            note_id=note_id,
            title=body.title,
            body=body.body,
            tags=body.tags,
            visibility=body.visibility,
            note_password_hash=new_hash,
        )
        return NoteResponse.from_domain(note)
    except NoteNotFoundError:
        raise HTTPException(status_code=404, detail=f"Note {note_id!r} not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


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


@router.post("/{note_id}/emergency-unlock", response_model=NoteResponse)
def emergency_unlock(
    note_id: str,
    body: EmergencyUnlockRequest,
    user_id: str = Depends(get_current_user),
    service: NoteService = Depends(get_note_service),
):
    """Emergency unlock: verify account password, clear note_password_hash. (FR-01)"""
    from app.routers.auth import verify_user_password
    if not verify_user_password(user_id, body.account_password):
        raise HTTPException(status_code=403, detail="Incorrect account password")
    try:
        note = service.update_note(
            user_id=user_id,
            note_id=note_id,
            note_password_hash=None,
        )
        return NoteResponse.from_domain(note)
    except NoteNotFoundError:
        raise HTTPException(status_code=404, detail=f"Note {note_id!r} not found")
    except AccessDeniedError:
        raise HTTPException(status_code=403, detail="Access denied")
