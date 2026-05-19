import json
import os
import shutil
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional

from .abstract_note_repository import AbstractNoteRepository
from ..note import Note
from ..exceptions import NoteNotFoundError, StorageIOError, StorageCorruptionError


README_BACKUP_COUNT = 3


class JsonFileNoteRepository(AbstractNoteRepository):
    def __init__(self, path: str = "astranotes_data.json"):
        self.path = path
        self.lock = Lock()
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not os.path.exists(self.path):
            try:
                self._atomic_save({"notes": [], "history": []})
            except Exception as exc:
                raise StorageIOError(str(exc))

    def _load(self) -> Dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            self._restore_backup()
            raise StorageCorruptionError("JSON corruption detected") from exc
        except OSError as exc:
            raise StorageIOError("Could not read notes store") from exc

    def _atomic_save(self, data: Dict) -> None:
        tmp_path = f"{self.path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.path)
            self._rotate_backups()
        except OSError as exc:
            raise StorageIOError("Could not write notes store") from exc

    def _rotate_backups(self):
        for i in range(README_BACKUP_COUNT - 1, 0, -1):
            from_path = f"{self.path}.bak.{i}"
            to_path = f"{self.path}.bak.{i+1}"
            if os.path.exists(from_path):
                shutil.copy2(from_path, to_path)
        if os.path.exists(self.path):
            shutil.copy2(self.path, f"{self.path}.bak.1")

    def _restore_backup(self):
        for i in range(1, README_BACKUP_COUNT + 1):
            candidate = f"{self.path}.bak.{i}"
            if os.path.exists(candidate):
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        return json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue
        raise StorageCorruptionError("No valid backup found")

    def _save(self, data: Dict) -> None:
        with self.lock:
            self._atomic_save(data)

    def create(self, note: Note) -> Note:
        data = self._load()
        data["notes"].append(note.to_dict())
        note_snapshot = note.to_dict()
        data["history"].append({"note_id": note.id, "version": note.version, "data": note_snapshot, "change_type": "create"})
        self._save(data)
        return note

    def get(self, note_id: str) -> Note:
        data = self._load()
        raw = next((n for n in data["notes"] if n["id"] == note_id), None)
        if not raw:
            raise NoteNotFoundError(f"Note {note_id} not found")
        return Note.from_dict(raw)

    def list(self, filters: Optional[Dict] = None) -> List[Note]:
        data = self._load()
        notes = [Note.from_dict(n) for n in data.get("notes", [])]
        if not filters:
            return notes
        result = notes
        if "tags" in filters:
            tags = set(filters["tags"])
            result = [n for n in result if tags.intersection(set(n.tags))]
        if "visibility" in filters:
            result = [n for n in result if n.visibility == filters["visibility"]]
        if "author_id" in filters:
            result = [n for n in result if n.author_id == filters["author_id"]]
        return result

    def update(self, note: Note) -> Note:
        data = self._load()
        existing = next((n for n in data["notes"] if n["id"] == note.id), None)
        if not existing:
            raise NoteNotFoundError(f"Note {note.id} not found")
        idx = next(i for i, n in enumerate(data["notes"]) if n["id"] == note.id)
        data["notes"][idx] = note.to_dict()
        data["history"].append({"note_id": note.id, "version": note.version, "data": note.to_dict(), "change_type": "update"})
        self._save(data)
        return note

    def delete(self, note_id: str) -> bool:
        data = self._load()
        before = len(data.get("notes", []))
        data["notes"] = [n for n in data.get("notes", []) if n["id"] != note_id]
        deleted = len(data["notes"]) < before
        if deleted:
            data["history"].append({"note_id": note_id, "version": -1, "data": {}, "change_type": "delete"})
            self._save(data)
        return deleted

    def add_version_snapshot(self, note: Note, change_type: str, actor_id: Optional[str] = None) -> None:
        data = self._load()
        data.setdefault("history", []).append({
            "note_id": note.id,
            "version": note.version,
            "data": note.to_dict(),
            "change_type": change_type,
            "actor_id": actor_id,
            "at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        })
        self._save(data)

    def get_versions(self, note_id: str) -> List[Dict]:
        data = self._load()
        return [h for h in data.get("history", []) if h["note_id"] == note_id]

    def revert_to_version(self, note_id: str, version: int, actor_id: Optional[str] = None) -> Note:
        data = self._load()
        history_items = [h for h in data.get("history", []) if h["note_id"] == note_id and h["version"] == version]
        if not history_items:
            raise NoteNotFoundError(f"Version {version} for note {note_id} not found")
        snapshot = history_items[-1]["data"]
        note = Note.from_dict(snapshot)
        note.version += 1
        note.updated_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        # update note in notes list
        idx = next((i for i, n in enumerate(data.get("notes", [])) if n["id"] == note_id), None)
        if idx is not None:
            data["notes"][idx] = note.to_dict()
        else:
            data.setdefault("notes", []).append(note.to_dict())
        data.setdefault("history", []).append({
            "note_id": note.id,
            "version": note.version,
            "data": note.to_dict(),
            "change_type": "revert",
            "actor_id": actor_id,
            "at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        })
        self._save(data)
        return note