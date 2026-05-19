import os
import tempfile

from AstraNotes_v1.repositories.json_file_note_repository import JsonFileNoteRepository
from AstraNotes_v1.history.version_history import VersionHistory
from AstraNotes_v1.note import Note


def test_version_history_integration():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        history = VersionHistory(repo)

        note = Note(title="t", body="b", author_id="u1")
        repo.create(note)
        note.body = "b2"
        note.version += 1
        repo.update(note)

        events = history.get_history(note.id)
        assert len(events) >= 2

        restored = history.revert(note.id, 1, actor_id="u1")
        assert restored.body == "b"


def test_version_history_records_create_and_update():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        history = VersionHistory(repo)

        note = Note(title="t", body="v1", author_id="u1")
        repo.create(note)
        history.add_entry(note, "create", actor_id="u1")

        note.body = "v2"
        note.version += 1
        repo.update(note)
        history.add_entry(note, "update", actor_id="u1")

        events = history.get_history(note.id)
        assert len(events) >= 2


def test_version_history_revert_restores_body():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        history = VersionHistory(repo)

        note = Note(title="t", body="original", author_id="u1")
        repo.create(note)
        history.add_entry(note, "create", actor_id="u1")

        note.body = "modified"
        note.version += 1
        repo.update(note)
        history.add_entry(note, "update", actor_id="u1")

        restored = history.revert(note.id, 1, actor_id="u1")
        assert restored.body == "original"
