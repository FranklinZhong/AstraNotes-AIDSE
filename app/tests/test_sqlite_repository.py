"""Unit tests for SqliteNoteRepository — Sprint 7.
Test classification: unit (repository in isolation, in-memory SQLite).
Test timing: written before implementation (TDD Step A1-1).
"""
import pytest
from AstraNotes_v1.note import Note
from AstraNotes_v1.exceptions import NoteNotFoundError
from app.db.sqlite_repository import SqliteNoteRepository


@pytest.fixture
def repo():
    """Fresh in-memory SQLite database per test."""
    return SqliteNoteRepository("sqlite:///:memory:")


@pytest.fixture
def sample_note():
    return Note(title="Test Note", body="Hello world", author_id="user-alice")


# TSQ-01
def test_create_returns_same_note(repo, sample_note):
    result = repo.create(sample_note)
    assert result.id == sample_note.id
    assert result.title == "Test Note"
    assert result.author_id == "user-alice"


# TSQ-02
def test_get_after_create(repo, sample_note):
    repo.create(sample_note)
    fetched = repo.get(sample_note.id)
    assert fetched.title == "Test Note"
    assert fetched.body == "Hello world"


# TSQ-03
def test_get_nonexistent_raises_note_not_found(repo):
    with pytest.raises(NoteNotFoundError):
        repo.get("nonexistent-id")


# TSQ-04
def test_list_empty_returns_empty_list(repo):
    assert repo.list() == []


# TSQ-05
def test_list_returns_all_notes(repo):
    repo.create(Note(title="Note 1", author_id="user-alice"))
    repo.create(Note(title="Note 2", author_id="user-alice"))
    repo.create(Note(title="Note 3", author_id="user-alice"))
    result = repo.list()
    assert len(result) == 3


# TSQ-06
def test_list_with_author_id_filter(repo):
    repo.create(Note(title="Alice's note", author_id="user-alice"))
    repo.create(Note(title="Bob's note", author_id="user-bob"))
    result = repo.list({"author_id": "user-alice"})
    assert len(result) == 1
    assert result[0].author_id == "user-alice"


# TSQ-07
def test_update_modifies_fields(repo, sample_note):
    repo.create(sample_note)
    sample_note.title = "Updated Title"
    updated = repo.update(sample_note)
    fetched = repo.get(sample_note.id)
    assert fetched.title == "Updated Title"


# TSQ-08
def test_update_nonexistent_raises_note_not_found(repo):
    fake = Note(title="Fake", author_id="user-x")
    with pytest.raises(NoteNotFoundError):
        repo.update(fake)


# TSQ-09
def test_delete_returns_true(repo, sample_note):
    repo.create(sample_note)
    assert repo.delete(sample_note.id) is True
    with pytest.raises(NoteNotFoundError):
        repo.get(sample_note.id)


# TSQ-10
def test_delete_nonexistent_returns_false(repo):
    assert repo.delete("nonexistent-id") is False


# TSQ-11
def test_tags_round_trip(repo):
    note = Note(title="Tagged", author_id="user-x", tags=["python", "testing"])
    repo.create(note)
    fetched = repo.get(note.id)
    assert fetched.tags == ["python", "testing"]


# TSQ-12
def test_version_field_persisted(repo, sample_note):
    sample_note.version = 3
    repo.create(sample_note)
    fetched = repo.get(sample_note.id)
    assert fetched.version == 3


# TSQ-13
def test_add_version_snapshot_does_not_crash(repo, sample_note):
    repo.create(sample_note)
    repo.add_version_snapshot(sample_note, "create", actor_id="user-alice")  # must not raise
    # no assertion needed, just verifying no exception
