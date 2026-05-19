from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict

from ..note import Note
from ..repositories.abstract_note_repository import AbstractNoteRepository


@dataclass
class VersionEntry:
    note_id: str
    version: int
    data: Dict
    change_type: str
    actor_id: Optional[str] = None
    at: str = ""


class VersionHistory:
    """High-level version history manager around repository history storage."""

    def __init__(self, repository: AbstractNoteRepository):
        self.repository = repository

    def add_entry(self, note: Note, change_type: str, actor_id: Optional[str] = None):
        self.repository.add_version_snapshot(note, change_type, actor_id)

    def get_history(self, note_id: str) -> List[VersionEntry]:
        raw = self.repository.get_versions(note_id)
        return [VersionEntry(**entry) for entry in raw]

    def revert(self, note_id: str, version: int, actor_id: Optional[str] = None) -> Note:
        return self.repository.revert_to_version(note_id, version, actor_id)
