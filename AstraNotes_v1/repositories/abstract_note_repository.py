from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from ..note import Note


class AbstractNoteRepository(ABC):
    """Repository interface for note persistence."""

    @abstractmethod
    def create(self, note: Note) -> Note:
        ...

    @abstractmethod
    def get(self, note_id: str) -> Note:
        ...

    @abstractmethod
    def list(self, filters: Optional[Dict] = None) -> List[Note]:
        ...

    @abstractmethod
    def update(self, note: Note) -> Note:
        ...

    @abstractmethod
    def delete(self, note_id: str) -> bool:
        ...

    @abstractmethod
    def add_version_snapshot(self, note: Note, change_type: str, actor_id: Optional[str] = None) -> None:
        ...

    @abstractmethod
    def get_versions(self, note_id: str) -> List[Dict]:
        ...

    @abstractmethod
    def revert_to_version(self, note_id: str, version: int, actor_id: Optional[str] = None) -> Note:
        ...
