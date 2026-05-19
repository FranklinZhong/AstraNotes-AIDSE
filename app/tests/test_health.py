"""Smoke tests — GET /health"""


def test_health_check_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_check_includes_service_name(client):
    resp = client.get("/health")
    assert "AstraNotes" in resp.json()["service"]
