"""Notes API integration tests — aligned to User Stories US-01 to US-05."""
import pytest


def test_us01_create_note_with_valid_title_returns_201(client, auth_headers):
    resp = client.post("/notes/", json={"title": "My Note"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Note"
    assert data["body"] == ""
    assert data["visibility"] == "public"  # NoteCreate defaults to "public" (ADR-WEB-01)


def test_us01_create_note_with_empty_title_returns_422(client, auth_headers):
    """Pydantic validation rejects empty title even before service layer."""
    resp = client.post("/notes/", json={"title": ""}, headers=auth_headers)
    assert resp.status_code == 422


def test_us05_list_notes_returns_empty_list_initially(client, auth_headers):
    resp = client.get("/notes/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["notes"] == []
    assert resp.json()["total"] == 0


def test_us02_update_note_increments_version(client, auth_headers):
    create = client.post("/notes/", json={"title": "Draft"}, headers=auth_headers)
    note_id = create.json()["id"]
    resp = client.patch(f"/notes/{note_id}", json={"title": "Final"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["version"] == 2


def test_us03_delete_note_returns_204(client, auth_headers):
    create = client.post("/notes/", json={"title": "Temp"}, headers=auth_headers)
    note_id = create.json()["id"]
    resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 204


# ── New tests TNA-01 through TNA-04 ──────────────────────────────────────────

def test_create_note_response_has_author_id(client, auth_headers):
    """TNA-01: create note response includes author_id and version=1. FR-01 / US-01."""
    resp = client.post("/notes/", json={"title": "Author Test"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["author_id"] == "testuser"
    assert data["version"] == 1


def test_get_note_by_id_returns_200(client, auth_headers):
    """TNA-02: GET /notes/{id} returns 200 after creation. FR-01 / US-01."""
    create_resp = client.post("/notes/", json={"title": "Get Me"}, headers=auth_headers)
    note_id = create_resp.json()["id"]
    resp = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get Me"


def test_get_nonexistent_note_returns_404(client, auth_headers):
    """TNA-03: unknown note id returns 404. FR-01."""
    resp = client.get("/notes/nonexistent-id-12345", headers=auth_headers)
    assert resp.status_code == 404


def test_list_only_returns_own_notes(client, auth_headers):
    """TNA-04: private notes are not visible to other users. FR-05 / US-05."""
    client.post("/notes/", json={"title": "Alice's private note"}, headers=auth_headers)

    client.post("/auth/register", json={"username": "userB", "password": "pw123"})
    login_resp = client.post("/auth/login", json={"username": "userB", "password": "pw123"})
    b_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    resp = client.get("/notes/", headers=b_headers)
    assert resp.status_code == 200
    assert resp.json()["notes"] == []
    assert resp.json()["total"] == 0


# ── Week 9 improved tests ─────────────────────────────────────────────────────

def test_patch_with_whitespace_only_title_returns_422(client, auth_headers):
    """TNA-05: PATCH with whitespace-only title must be rejected with 422 (FR-01/US-02).

    NoteUpdate schema intentionally omits title validation so partial updates work.
    Rejection happens via Note.patch() raising ValidationError, caught in the router
    and re-raised as HTTP 422. This test is the only regression guard for that path.
    """
    create = client.post("/notes/", json={"title": "Valid Title"}, headers=auth_headers)
    note_id = create.json()["id"]
    resp = client.patch(f"/notes/{note_id}", json={"title": "   "}, headers=auth_headers)
    assert resp.status_code == 422


def test_tags_filter_returns_matching_notes(client, auth_headers):
    """TNA-06: GET /notes/?tags=X returns only notes that include tag X (FR-04/US-05)."""
    client.post("/notes/", json={"title": "Tagged", "tags": ["python", "testing"], "visibility": "public"}, headers=auth_headers)
    client.post("/notes/", json={"title": "Untagged", "tags": [], "visibility": "public"}, headers=auth_headers)
    resp = client.get("/notes/?tags=python", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    titles = {n["title"] for n in data["notes"]}
    assert "Tagged" in titles
    assert "Untagged" not in titles


def test_tags_filter_returns_empty_when_no_match(client, auth_headers):
    """TNA-07: ?tags=nonexistent returns empty list, not a server error (FR-04).

    High line coverage on the filter block still leaves this no-match path untested.
    Without this test, removing the early-return guard could silently break the API.
    """
    client.post("/notes/", json={"title": "Note A", "tags": ["python"], "visibility": "public"}, headers=auth_headers)
    resp = client.get("/notes/?tags=doesnotexist", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["notes"] == []
    assert resp.json()["total"] == 0


def test_tags_filter_is_case_sensitive(client, auth_headers):
    """TNA-08: tag matching is case-sensitive per FR-04 spec (Python vs python)."""
    client.post("/notes/", json={"title": "Lower", "tags": ["python"], "visibility": "public"}, headers=auth_headers)
    resp = client.get("/notes/?tags=Python", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_tags_filter_requires_all_tags_present(client, auth_headers):
    """TNA-09: ?tags=a&tags=b returns only notes containing BOTH a and b (AND semantics, FR-04).

    The filter uses set.issubset() — notes with only one matching tag must be excluded.
    Without this test, changing issubset() to any() (OR logic) would go undetected.
    """
    client.post("/notes/", json={"title": "Both", "tags": ["python", "testing"], "visibility": "public"}, headers=auth_headers)
    client.post("/notes/", json={"title": "One only", "tags": ["python"], "visibility": "public"}, headers=auth_headers)
    resp = client.get("/notes/?tags=python&tags=testing", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    titles = {n["title"] for n in data["notes"]}
    assert "Both" in titles
    assert "One only" not in titles


# ── Note password access control (TNA-10 / TNA-11 / TNA-12) ──────────────────

def test_get_private_note_without_password_returns_401(client, auth_headers):
    """TNA-10: GET /notes/{id} on a password-protected private note with no X-Note-Password returns 401.

    _require_note_password() raises 401 when note_password_hash is set but no password header
    is provided. The note must be visibility='private' — public notes skip the password check.
    This test is the primary regression guard for that branch.
    """
    create = client.post(
        "/notes/",
        json={"title": "Secret", "visibility": "private", "note_password": "hunter2"},
        headers=auth_headers,
    )
    note_id = create.json()["id"]
    resp = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 401


def test_get_private_note_with_wrong_password_returns_403(client, auth_headers):
    """TNA-11: GET /notes/{id} on a password-protected private note with an incorrect X-Note-Password returns 403.

    _require_note_password() raises 403 when the provided password does not match the stored
    bcrypt hash. Without this test, removing the verify() call would go undetected.
    """
    create = client.post(
        "/notes/",
        json={"title": "Secret", "visibility": "private", "note_password": "hunter2"},
        headers=auth_headers,
    )
    note_id = create.json()["id"]
    resp = client.get(f"/notes/{note_id}", headers={**auth_headers, "X-Note-Password": "wrong"})
    assert resp.status_code == 403


def test_get_private_note_with_correct_password_returns_200(client, auth_headers):
    """TNA-12: GET /notes/{id} with the correct X-Note-Password returns 200 with full body.

    This is the success path of _require_note_password(). Without this test, the password
    verification could always raise 403 and the happy path would go untested.
    """
    create = client.post(
        "/notes/",
        json={"title": "Secret", "body": "my secret body", "visibility": "private", "note_password": "hunter2"},
        headers=auth_headers,
    )
    note_id = create.json()["id"]
    resp = client.get(f"/notes/{note_id}", headers={**auth_headers, "X-Note-Password": "hunter2"})
    assert resp.status_code == 200
    assert resp.json()["body"] == "my secret body"


# ── AccessDeniedError → 403 for PATCH and DELETE (TNA-13 / TNA-14) ───────────

def test_patch_note_by_non_owner_returns_403(client, auth_headers):
    """TNA-13: PATCH /notes/{id} by a user who is not the author returns 403.

    NoteService.update_note() raises AccessDeniedError via PrivacyPolicy.can_update().
    The router maps this to HTTP 403. Without this test, removing that exception handler
    would silently allow unauthorized edits.
    """
    create = client.post("/notes/", json={"title": "Original", "visibility": "public"}, headers=auth_headers)
    note_id = create.json()["id"]

    client.post("/auth/register", json={"username": "userB", "password": "pw123"})
    login = client.post("/auth/login", json={"username": "userB", "password": "pw123"})
    b_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = client.patch(f"/notes/{note_id}", json={"title": "Hijacked"}, headers=b_headers)
    assert resp.status_code == 403


def test_delete_note_by_non_owner_returns_403(client, auth_headers):
    """TNA-14: DELETE /notes/{id} by a non-owner returns 403.

    Same AccessDeniedError → 403 path as PATCH, exercised through the DELETE router.
    """
    create = client.post("/notes/", json={"title": "Do not delete", "visibility": "public"}, headers=auth_headers)
    note_id = create.json()["id"]

    client.post("/auth/register", json={"username": "userC", "password": "pw456"})
    login = client.post("/auth/login", json={"username": "userC", "password": "pw456"})
    c_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = client.delete(f"/notes/{note_id}", headers=c_headers)
    assert resp.status_code == 403


# ── Unicode title validation (TNA-15) ────────────────────────────────────────

def test_create_note_with_non_breaking_space_title_returns_422(client, auth_headers):
    """TNA-15: Title consisting only of non-breaking spaces (U+00A0) must be rejected.

    str.strip() does not remove U+00A0 — a title of '\\u00a0' would silently pass
    the original validator. The fix uses re.search(r'\\S', v) which treats all
    Unicode whitespace as whitespace, not just ASCII.
    """
    resp = client.post("/notes/", json={"title": " "}, headers=auth_headers)
    assert resp.status_code == 422


# -- Emergency unlock (TNA-16 / TNA-17 / TNA-18) --

def test_emergency_unlock_with_correct_account_password_clears_note_password(client, auth_headers):
    """TNA-16: POST /notes/{id}/emergency-unlock with correct account password clears
    note_password_hash and returns 200 with is_protected=false. (FR-08)

    After unlock the note must be accessible via GET without X-Note-Password.
    """
    create = client.post(
        "/notes/",
        json={"title": "Locked", "visibility": "private", "note_password": "secret"},
        headers=auth_headers,
    )
    note_id = create.json()["id"]
    assert create.json()["is_protected"] is True

    unlock = client.post(
        f"/notes/{note_id}/emergency-unlock",
        json={"account_password": "testpass"},
        headers=auth_headers,
    )
    assert unlock.status_code == 200
    assert unlock.json()["is_protected"] is False

    get_resp = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert get_resp.status_code == 200


def test_emergency_unlock_with_wrong_account_password_returns_403(client, auth_headers):
    """TNA-17: POST /notes/{id}/emergency-unlock with wrong account password returns 403.
    (FR-08)

    verify_user_password() fails -> HTTPException 403 before any note mutation occurs.
    """
    create = client.post(
        "/notes/",
        json={"title": "Locked", "visibility": "private", "note_password": "secret"},
        headers=auth_headers,
    )
    note_id = create.json()["id"]

    resp = client.post(
        f"/notes/{note_id}/emergency-unlock",
        json={"account_password": "wrongpass"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


def test_emergency_unlock_on_nonexistent_note_returns_404(client, auth_headers):
    """TNA-18: POST /notes/{id}/emergency-unlock on unknown note returns 404. (FR-08)

    Account password is verified first; NoteNotFoundError from service -> HTTP 404.
    """
    resp = client.post(
        "/notes/nonexistent-id/emergency-unlock",
        json={"account_password": "testpass"},
        headers=auth_headers,
    )
    assert resp.status_code == 404
