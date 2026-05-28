"""Note request and response schemas (Pydantic)."""
from __future__ import annotations

import re
from typing import List, Optional
from pydantic import BaseModel, field_validator


class NoteCreate(BaseModel):
    """Request body for POST /notes."""
    title: str
    body: str = ""
    tags: List[str] = []
    visibility: str = "public"
    note_password: Optional[str] = None  # required when visibility=="private"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        # re.search(r'\S') catches all Unicode whitespace, not just ASCII (str.strip() misses U+00A0)
        if not v or not re.search(r'\S', v):
            raise ValueError("title must contain at least one non-whitespace character")
        return v

    @field_validator("visibility")
    @classmethod
    def visibility_valid(cls, v: str) -> str:
        if v not in {"private", "public"}:
            raise ValueError("visibility must be 'private' or 'public'")
        return v


class NoteUpdate(BaseModel):
    """Request body for PATCH /notes/{id}."""
    title: Optional[str] = None
    body: Optional[str] = None
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None
    note_password: Optional[str] = None  # new note password to set (or clear when visibility→public)


class NoteResponse(BaseModel):
    """Response schema for a single note."""
    id: str
    title: str
    body: str
    tags: List[str] = []
    visibility: str
    author_id: Optional[str]
    created_at: str
    updated_at: str
    version: int
    is_protected: bool = False  # True when note has a note_password_hash set

    @classmethod
    def from_domain(cls, note) -> "NoteResponse":
        """Convert a domain Note object to a NoteResponse."""
        return cls(
            id=note.id,
            title=note.title,
            body=note.body,
            tags=list(getattr(note, "tags", [])),
            visibility=note.visibility,
            author_id=note.author_id,
            created_at=note.created_at,
            updated_at=note.updated_at,
            version=note.version,
            is_protected=bool(getattr(note, "note_password_hash", None)),
        )


class NoteListResponse(BaseModel):
    """Response schema for GET /notes."""
    notes: List[NoteResponse]
    total: int


class EmergencyUnlockRequest(BaseModel):
    """Request body for POST /notes/{id}/emergency-unlock."""
    account_password: str
