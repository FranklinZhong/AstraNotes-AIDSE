"""SqliteNoteRepository — SQLAlchemy Core implementation. Sprint 7/8."""
from __future__ import annotations

import json
from datetime import datetime, timezone
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
            Column("id",                 Text, primary_key=True),
            Column("title",              Text, nullable=False),
            Column("body",               Text, default=""),
            Column("visibility",         Text, default="public"),
            Column("author_id",          Text),
            Column("created_at",         Text),
            Column("updated_at",         Text),
            Column("version",            Integer, default=1),
            Column("tags",               Text, default="[]"),
            Column("note_password_hash", Text, nullable=True),
        )
        self._versions = Table(
            "note_versions", meta,
            Column("id",          Integer, primary_key=True, autoincrement=True),
            Column("note_id",     Text, nullable=False),
            Column("version",     Integer, nullable=False),
            Column("data",        Text, nullable=False),
            Column("change_type", Text, nullable=False),
            Column("actor_id",    Text),
            Column("at",          Text),
        )
        meta.create_all(self._engine)

    # ── helpers ────────────────────────────────────────────────────────────

    def _to_row(self, note: Note) -> Dict:
        return {
            "id":                 note.id,
            "title":              note.title,
            "body":               note.body,
            "visibility":         note.visibility,
            "author_id":          note.author_id,
            "created_at":         note.created_at,
            "updated_at":         note.updated_at,
            "version":            note.version,
            "tags":               json.dumps(note.tags),
            "note_password_hash": note.note_password_hash,
        }

    def _from_row(self, row) -> Note:
        d = dict(row._mapping)
        tags = json.loads(d.get("tags") or "[]")
        return Note(
            id=d["id"],
            title=d["title"],
            body=d.get("body", ""),
            visibility=d.get("visibility", "public"),
            author_id=d.get("author_id"),
            tags=tags,
            metadata={},
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            version=int(d.get("version", 1)),
            note_password_hash=d.get("note_password_hash"),
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
        with self._engine.connect() as conn:
            conn.execute(insert(self._versions).values(
                note_id=note.id,
                version=note.version,
                data=json.dumps({
                    "id": note.id,
                    "title": note.title,
                    "body": note.body,
                    "visibility": note.visibility,
                    "author_id": note.author_id,
                    "tags": note.tags,
                    "version": note.version,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                }),
                change_type=change_type,
                actor_id=actor_id,
                at=datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
            ))
            conn.commit()

    def get_versions(self, note_id: str) -> List[Dict]:
        with self._engine.connect() as conn:
            rows = conn.execute(
                select(self._versions)
                .where(self._versions.c.note_id == note_id)
                .order_by(self._versions.c.version)
            ).fetchall()
        return [
            {
                "note_id": r.note_id,
                "version": r.version,
                "data": json.loads(r.data),
                "change_type": r.change_type,
                "actor_id": r.actor_id,
                "at": r.at or "",
            }
            for r in rows
        ]

    def revert_to_version(
        self, note_id: str, version: int, actor_id: Optional[str] = None
    ) -> Note:
        current = self.get(note_id)  # raises NoteNotFoundError if note absent

        with self._engine.connect() as conn:
            row = conn.execute(
                select(self._versions)
                .where(self._versions.c.note_id == note_id)
                .where(self._versions.c.version == version)
            ).first()

        if row is None:
            raise NoteNotFoundError(
                f"Version {version} of note {note_id!r} not found in history"
            )

        snapshot = json.loads(row.data)
        restored = Note(
            id=current.id,
            title=snapshot["title"],
            body=snapshot.get("body", ""),
            visibility=snapshot.get("visibility", "private"),
            author_id=current.author_id,
            tags=snapshot.get("tags", []),
            metadata={},
            created_at=current.created_at,
            updated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
            version=current.version + 1,
        )
        self.update(restored)
        self.add_version_snapshot(restored, "revert", actor_id=actor_id)
        return restored
