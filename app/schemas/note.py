"""Note request and response schemas (Pydantic)."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, field_validator


class NoteCreate(BaseModel):
    """Request body for POST /notes."""
    title: str
    body: str = ""
    visibility: str = "private"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must be a non-empty string")
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
    visibility: Optional[str] = None


class NoteResponse(BaseModel):
    """Response schema for a single note."""
    id: str
    title: str
    body: str
    visibility: str
    author_id: Optional[str]
    created_at: str
    updated_at: str
    version: int

    @classmethod
    def from_domain(cls, note) -> "NoteResponse":
        """Convert a domain Note object to a NoteResponse."""
        return cls(
            id=note.id,
            title=note.title,
            body=note.body,
            visibility=note.visibility,
            author_id=note.author_id,
            created_at=note.created_at,
            updated_at=note.updated_at,
            version=note.version,
        )


class NoteListResponse(BaseModel):
    """Response schema for GET /notes."""
    notes: List[NoteResponse]
    total: int
