import os
import tempfile

import pytest

from AstraNotes_v1.repositories.json_file_note_repository import JsonFileNoteRepository
from AstraNotes_v1.note import Note
from AstraNotes_v1.exceptions import NoteNotFoundError


def test_repository_crud_cycle():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "notes.json")
        repo = JsonFileNoteRepository(path)

        note = Note(title="t", body="b", author_id="u1")
        created = repo.create(note)
        assert created.id == note.id

        loaded = repo.get(note.id)
        assert loaded.title == "t"

        notes = repo.list()
        assert len(notes) == 1

        loaded.body = "updated"
        updated = repo.update(loaded)
        assert updated.body == "updated"

        assert repo.delete(note.id)
        with pytest.raises(NoteNotFoundError):
            repo.get(note.id)


def test_repository_delete_nonexisting_returns_false():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        assert not repo.delete("missing")


def test_repository_get_nonexistent_raises():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        with pytest.raises(NoteNotFoundError):
            repo.get("nonexistent-id")


def test_repository_update_nonexistent_raises():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        ghost = Note(title="t", body="b", author_id="u1")
        with pytest.raises(NoteNotFoundError):
            repo.update(ghost)


def test_repository_list_returns_all():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        for i in range(3):
            repo.create(Note(title=f"t{i}", body=f"b{i}", author_id="u1"))
        assert len(repo.list()) == 3


def test_repository_persistence_across_instances():
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "notes.json")
        note = Note(title="persist", body="test", author_id="u1")
        JsonFileNoteRepository(path).create(note)
        reloaded = JsonFileNoteRepository(path).get(note.id)
        assert reloaded.title == "persist"


def test_repository_version_snapshot_stored():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        note = Note(title="t", body="b", author_id="u1")
        repo.create(note)
        repo.add_version_snapshot(note, "create")
        versions = repo.get_versions(note.id)
        assert len(versions) >= 1
