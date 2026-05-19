"""Auth endpoint integration tests — POST /auth/register and /auth/login."""


def test_register_new_user_returns_jwt(client):
    resp = client.post("/auth/register", json={"username": "alice", "password": "pw"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_username_returns_400(client):
    client.post("/auth/register", json={"username": "alice", "password": "pw"})
    resp = client.post("/auth/register", json={"username": "alice", "password": "pw2"})
    assert resp.status_code == 400


def test_login_valid_credentials_returns_jwt(client):
    client.post("/auth/register", json={"username": "alice", "password": "pw"})
    resp = client.post("/auth/login", json={"username": "alice", "password": "pw"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_returns_401(client):
    client.post("/auth/register", json={"username": "alice", "password": "pw"})
    resp = client.post("/auth/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401


def test_notes_without_token_returns_401(client):
    """Notes endpoints require authentication."""
    resp = client.get("/notes/")
    assert resp.status_code == 401
