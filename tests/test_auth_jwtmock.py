import pytest

def test_invalid_mock_token_rejected(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    resp = client.post("/api/v1/listings/", json={"title": "bad", "price": 1}, headers=headers)
    assert resp.status_code == 401