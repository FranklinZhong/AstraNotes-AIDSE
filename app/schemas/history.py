"""Version history request and response schemas (Pydantic)."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class VersionEntryResponse(BaseModel):
    note_id: str
    version: int
    change_type: str
    at: str
    actor_id: Optional[str] = None
    title: str = ""


class VersionHistoryResponse(BaseModel):
    note_id: str
    versions: List[VersionEntryResponse]
    total: int
