import pytest

from AstraNotes_v1.note import Note
from AstraNotes_v1.exceptions import ValidationError


def test_note_creation_defaults():
    note = Note(title="title", body="body", author_id="user1")
    assert note.id
    assert note.title == "title"
    assert note.body == "body"
    assert note.visibility == "private"
    assert note.version == 1


def test_note_from_dict_and_to_dict():
    note = Note(title="a", body="b", author_id="user1")
    payload = note.to_dict()
    converted = Note.from_dict(payload)
    assert converted.title == note.title
    assert converted.author_id == note.author_id


def test_note_invalid_visibility_raises():
    with pytest.raises(ValidationError):
        Note(title="t", body="b", visibility="secret", author_id="user1")


def test_note_empty_title_raises():
    with pytest.raises(ValidationError):
        Note(title="", body="b", author_id="user1")


def test_note_whitespace_only_title_raises():
    with pytest.raises(ValidationError):
        Note(title="   ", body="b", author_id="user1")


def test_note_tab_only_title_raises():
    with pytest.raises(ValidationError):
        Note(title="\t", body="b", author_id="user1")


def test_note_newline_only_title_raises():
    with pytest.raises(ValidationError):
        Note(title="\n", body="b", author_id="user1")


def test_note_empty_body_allowed():
    # FR-01: body is optional; empty string must be valid
    note = Note(title="t", body="", author_id="user1")
    assert note.body == ""


def test_note_patch_increments_version():
    note = Note(title="t", body="b", author_id="user1")
    assert note.version == 1
    note.patch(body="updated")
    assert note.version == 2


def test_note_patch_updates_tags():
    note = Note(title="t", body="b", author_id="user1")
    note.patch(tags=["uml", "week4"])
    assert note.tags == ["uml", "week4"]


def test_note_default_visibility_is_private():
    note = Note(title="t", body="b", author_id="user1")
    assert note.visibility == "private"
