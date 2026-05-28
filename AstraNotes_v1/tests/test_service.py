import os
import tempfile

import pytest

from AstraNotes_v1.repositories.json_file_note_repository import JsonFileNoteRepository
from AstraNotes_v1.services.note_service import NoteService
from AstraNotes_v1.exceptions import AccessDeniedError, NoteNotFoundError


def test_note_service_crud_and_security():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        service = NoteService(repo)

        note = service.create_note("u1", "title", "body", visibility="private")
        assert note.author_id == "u1"

        with pytest.raises(AccessDeniedError):
            service.get_note("u2", note.id)

        fetched = service.get_note("u1", note.id)
        assert fetched.title == "title"

        updated = service.update_note("u1", note.id, body="new")
        assert updated.body == "new"

        assert service.delete_note("u1", note.id)
        with pytest.raises(NoteNotFoundError):
            service.get_note("u1", note.id)


def test_note_service_revert():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        service = NoteService(repo)

        note = service.create_note("u1", "t", "b")
        service.update_note("u1", note.id, body="b2")
        history = repo.get_versions(note.id)
        assert len(history) >= 2

        reverted = service.revert_note("u1", note.id, 1)
        assert reverted.body == "b"


def test_service_list_only_returns_own_notes():
    """list_notes() filters by author_id — owner-only access for all notes (ADR-WEB-01).
    Public visibility does NOT make notes cross-user visible; it only controls
    whether a note-level password is required (see ADR-PWD-01).
    """
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        service = NoteService(repo)

        service.create_note("u1", "private note", "secret", visibility="private")
        service.create_note("u1", "public note", "visible", visibility="public")

        visible = service.list_notes("u2")
        assert len(visible) == 0  # u2 sees no notes from u1; all notes are owner-only


def test_service_mark_note_private():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        service = NoteService(repo)

        note = service.create_note("u1", "t", "b", visibility="public")
        updated = service.update_note("u1", note.id, visibility="private")
        assert updated.visibility == "private"


def test_service_update_denied_for_non_author():
    with tempfile.TemporaryDirectory() as td:
        repo = JsonFileNoteRepository(os.path.join(td, "notes.json"))
        service = NoteService(repo)

        note = service.create_note("u1", "t", "b")
        with pytest.raises(AccessDeniedError):
            service.update_note("u2", note.id, body="hijack")
