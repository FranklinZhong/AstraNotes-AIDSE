"""SqliteNoteRepository — SQLAlchemy Core implementation. Sprint 7."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from sqlalchemy import (Column, Integer, MetaData, Table, Text, create_engine,
                        delete as sa_delete, insert, select, update as sa_update)

from AstraNotes_v1.exceptions import NoteNotFoundError
from AstraNotes_v1.note import Note
from AstraNotes_v1.repositories.abstract_note_repository import AbstractNoteRepository


class SqliteNoteRepository(AbstractNoteRepository):
    """SQLite-backed note repository using SQLAlchemy Core (no ORM).

    Args:
        db_url: SQLAlchemy database URL, e.g. "sqlite:///./notes.db"
                or "sqlite:///:memory:" for tests.
    """

    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, connect_args={"check_same_thread": False})
        meta = MetaData()
        self._notes = Table(
            "notes", meta,
            Column("id",          Text, primary_key=True),
            Column("title",       Text, nullable=False),
            Column("body",        Text, default=""),
            Column("visibility",  Text, default="private"),
            Column("author_id",   Text),
            Column("created_at",  Text),
            Column("updated_at",  Text),
            Column("version",     Integer, default=1),
            Column("tags",        Text, default="[]"),
        )
        meta.create_all(self._engine)

    # ── helpers ────────────────────────────────────────────────────────────

    def _to_row(self, note: Note) -> Dict:
        return {
            "id":         note.id,
            "title":      note.title,
            "body":       note.body,
            "visibility": note.visibility,
            "author_id":  note.author_id,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "version":    note.version,
            "tags":       json.dumps(note.tags),
        }

    def _from_row(self, row) -> Note:
        d = dict(row._mapping)
        tags = json.loads(d.get("tags") or "[]")
        # Note is a plain dataclass — all fields can be passed directly to constructor.
        return Note(
            id=d["id"],
            title=d["title"],
            body=d.get("body", ""),
            visibility=d.get("visibility", "private"),
            author_id=d.get("author_id"),
            tags=tags,
            metadata={},
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            version=int(d.get("version", 1)),
        )

    # ── CRUD ───────────────────────────────────────────────────────────────

    def create(self, note: Note) -> Note:
        with self._engine.connect() as conn:
            conn.execute(insert(self._notes).values(**self._to_row(note)))
            conn.commit()
        return note

    def get(self, note_id: str) -> Note:
        with self._engine.connect() as conn:
            row = conn.execute(
                select(self._notes).where(self._notes.c.id == note_id)
            ).first()
        if row is None:
            raise NoteNotFoundError(f"Note {note_id!r} not found")
        return self._from_row(row)

    def list(self, filters: Optional[Dict] = None) -> List[Note]:
        with self._engine.connect() as conn:
            rows = conn.execute(select(self._notes)).fetchall()
        notes = [self._from_row(r) for r in rows]
        if filters:
            for key, val in filters.items():
                notes = [n for n in notes if getattr(n, key, None) == val]
        return notes

    def update(self, note: Note) -> Note:
        self.get(note.id)  # raises NoteNotFoundError if absent
        with self._engine.connect() as conn:
            conn.execute(
                sa_update(self._notes)
                .where(self._notes.c.id == note.id)
                .values(**self._to_row(note))
            )
            conn.commit()
        return note

    def delete(self, note_id: str) -> bool:
        with self._engine.connect() as conn:
            result = conn.execute(
                sa_delete(self._notes).where(self._notes.c.id == note_id)
            )
            conn.commit()
        return result.rowcount > 0

    # ── Version history (Sprint 8) ─────────────────────────────────────────

    def add_version_snapshot(
        self, note: Note, change_type: str, actor_id: Optional[str] = None
    ) -> None:
        return None  # Sprint 8 — must not raise; called by NoteService.create_note/update_note

    def get_versions(self, note_id: str) -> List[Dict]:
        return []  # Sprint 8

    def revert_to_version(
        self, note_id: str, version: int, actor_id: Optional[str] = None
    ) -> Note:
        raise NotImplementedError("revert_to_version — Sprint 8")
