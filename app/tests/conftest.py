"""Shared pytest fixtures for API integration tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def clear_users():
    """Reset auth DB to isolated in-memory SQLite before each test."""
    from app.routers.auth import _reset_users_for_test
    _reset_users_for_test("sqlite:///:memory:")
    yield
    _reset_users_for_test("sqlite:///:memory:")


@pytest.fixture
def client():
    """FastAPI TestClient — no real server needed."""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Register a test user and return a JWT access token."""
    resp = client.post(
        "/auth/register",
        json={"username": "testuser", "password": "testpass"},
    )
    assert resp.status_code == 201
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Authorization header dict for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}


import uuid
from app.service_deps import get_note_service
from app.db.sqlite_repository import SqliteNoteRepository
from AstraNotes_v1.services.note_service import NoteService
from AstraNotes_v1.policies.privacy_policy import PrivacyPolicy


@pytest.fixture(autouse=True)
def reset_note_service():
    """Each test gets an isolated named in-memory SQLite database.

    Uses URI-format named memory databases (cache=shared) so multiple
    connections within one test share the same table — avoids the
    per-connection isolation of plain sqlite:///:memory:.
    """
    db_name = f"test_{uuid.uuid4().hex}"
    db_url = f"file:{db_name}?mode=memory&cache=shared&uri=true"
    repo = SqliteNoteRepository(f"sqlite+pysqlite:///{db_url}")
    svc = NoteService(repository=repo, policy=PrivacyPolicy())
    app.dependency_overrides[get_note_service] = lambda: svc
    yield
    app.dependency_overrides.pop(get_note_service, None)
