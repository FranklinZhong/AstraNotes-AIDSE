"""Version history API integration tests — Sprint 8. (FR-06)
Test classification: integration (HTTP endpoints end-to-end).
"""
import pytest


# TVH-01
def test_get_versions_after_create_returns_one_entry(client, auth_headers):
    """Creating a note automatically snapshots version 1."""
    create = client.post("/notes/", json={"title": "History Test"}, headers=auth_headers)
    note_id = create.json()["id"]
    resp = client.get(f"/notes/{note_id}/versions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["versions"][0]["change_type"] == "create"
    assert data["versions"][0]["title"] == "History Test"
    assert data["versions"][0]["version"] == 1


# TVH-02 (improved: assert on version number, not array position — same fix as TSQ-14)
def test_get_versions_after_update_returns_two_entries(client, auth_headers):
    """Updating a note adds a second snapshot, verifiable by version number not array index.

    Original test used versions[1] which couples the assertion to oldest-first sort order.
    If a future implementation returns newest-first the test fails for the wrong reason —
    ordering is an implementation detail, version numbers are the requirement (FR-06).
    """
    create = client.post("/notes/", json={"title": "v1 title"}, headers=auth_headers)
    note_id = create.json()["id"]
    client.patch(f"/notes/{note_id}", json={"title": "v2 title"}, headers=auth_headers)
    resp = client.get(f"/notes/{note_id}/versions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    by_version = {v["version"]: v for v in data["versions"]}
    assert 1 in by_version and 2 in by_version
    assert by_version[2]["change_type"] == "update"
    assert by_version[2]["title"] == "v2 title"


# TVH-03
def test_get_versions_for_nonexistent_note_returns_404(client, auth_headers):
    """Unknown note id returns 404 with detail message."""
    resp = client.get("/notes/nonexistent-id/versions", headers=auth_headers)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# TVH-04
def test_revert_to_valid_version_restores_title(client, auth_headers):
    """Revert to version 1 restores the original title as a new version."""
    create = client.post("/notes/", json={"title": "Original"}, headers=auth_headers)
    note_id = create.json()["id"]
    client.patch(f"/notes/{note_id}", json={"title": "Modified"}, headers=auth_headers)

    resp = client.post(f"/notes/{note_id}/revert/1", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Original"
    assert data["version"] == 3  # v1 create, v2 update, v3 revert


# TVH-05
def test_revert_to_nonexistent_version_returns_404(client, auth_headers):
    """Reverting to a version that was never snapshotted returns 404."""
    create = client.post("/notes/", json={"title": "Note"}, headers=auth_headers)
    note_id = create.json()["id"]
    resp = client.post(f"/notes/{note_id}/revert/99", headers=auth_headers)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
