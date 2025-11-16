import pytest

from app.database import get_db


def test_get_db_generator_closes():
    gen = get_db()
    db = next(gen)
    assert db is not None
    with pytest.raises(StopIteration):
        next(gen)


def test_health_endpoint(client):
    #assuming we still expose /api/v1/health
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"