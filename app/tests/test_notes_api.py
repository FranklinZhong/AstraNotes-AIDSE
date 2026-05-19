"""Notes API integration tests — aligned to User Stories US-01 to US-05.

Sprint 7: NoteService is now wired via dependency_overrides in conftest.py.
All skip decorators removed; 4 new tests added for TNA-01 through TNA-04.
"""
import pytest


def test_us01_create_note_with_valid_title_returns_201(client, auth_headers):
    resp = client.post("/notes/", json={"title": "My Note"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Note"
    assert data["body"] == ""
    assert data["visibility"] == "private"


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
    """TNA-01: 创建笔记响应包含 author_id 和 version=1。FR-01 / US-01."""
    resp = client.post("/notes/", json={"title": "Author Test"}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["author_id"] == "testuser"
    assert data["version"] == 1


def test_get_note_by_id_returns_200(client, auth_headers):
    """TNA-02: 创建后按 ID 获取笔记返回 200。FR-01 / US-01."""
    create_resp = client.post("/notes/", json={"title": "Get Me"}, headers=auth_headers)
    note_id = create_resp.json()["id"]
    resp = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get Me"


def test_get_nonexistent_note_returns_404(client, auth_headers):
    """TNA-03: 不存在的笔记 ID 返回 404。FR-01."""
    resp = client.get("/notes/nonexistent-id-12345", headers=auth_headers)
    assert resp.status_code == 404


def test_list_only_returns_own_notes(client, auth_headers):
    """TNA-04: 用户只能看到自己的 private 笔记，不能看到他人的。FR-05 / US-05."""
    # testuser 创建一条 private 笔记
    client.post("/notes/", json={"title": "Alice's private note"}, headers=auth_headers)

    # userB 注册并登录
    client.post("/auth/register", json={"username": "userB", "password": "pw123"})
    login_resp = client.post("/auth/login", json={"username": "userB", "password": "pw123"})
    b_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # userB 看到空列表（testuser 的 private 笔记对 userB 不可见）
    resp = client.get("/notes/", headers=b_headers)
    assert resp.status_code == 200
    assert resp.json()["notes"] == []
    assert resp.json()["total"] == 0
