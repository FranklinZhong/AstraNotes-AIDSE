import pytest

from AstraNotes_v1.policies.privacy_policy import PrivacyPolicy
from AstraNotes_v1.note import Note
from AstraNotes_v1.exceptions import AccessDeniedError


def test_privacy_can_read_public_by_owner():
    """Public visibility does not grant cross-user read access (ADR-WEB-01).
    PrivacyPolicy enforces owner-only access for all notes; 'public' only controls
    whether a note-level password is required.
    """
    note = Note(title="t", body="b", visibility="public", author_id="user1")
    assert PrivacyPolicy.can_read("user1", note)


def test_privacy_can_read_private_by_author():
    note = Note(title="t", body="b", visibility="private", author_id="user1")
    assert PrivacyPolicy.can_read("user1", note)


def test_privacy_can_read_private_denied():
    note = Note(title="t", body="b", visibility="private", author_id="user1")
    with pytest.raises(AccessDeniedError):
        PrivacyPolicy.can_read("user2", note)


def test_privacy_update_delete_permissions():
    note = Note(title="t", body="b", author_id="user1")
    assert PrivacyPolicy.can_update("user1", note)
    assert PrivacyPolicy.can_delete("user1", note)
    with pytest.raises(AccessDeniedError):
        PrivacyPolicy.can_update("user2", note)


def test_privacy_delete_denied_for_non_author():
    note = Note(title="t", body="b", author_id="user1")
    with pytest.raises(AccessDeniedError):
        PrivacyPolicy.can_delete("user2", note)


def test_privacy_can_read_public_denied_for_non_owner():
    """Unauthenticated and non-owner users cannot read public notes (ADR-WEB-01).
    All note access is owner-only regardless of visibility setting.
    """
    note = Note(title="t", body="b", visibility="public", author_id="user1")
    with pytest.raises(AccessDeniedError):
        PrivacyPolicy.can_read(None, note)
    with pytest.raises(AccessDeniedError):
        PrivacyPolicy.can_read("user2", note)
