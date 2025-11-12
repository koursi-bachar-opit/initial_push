import pytest

def test_auth_blocks_missing_token(client):
    resp = client.post("/api/v1/listings/", json={"title": "X", "price": 10})
    assert resp.status_code == 401

def test_auth_allows_provider_mock(client):
    headers = {"Authorization": "Bearer provider:alice"}
    resp = client.post("/api/v1/listings/", json={"title": "Mocked Listing", "price": 20}, headers=headers)
    assert resp.status_code in (200, 201)

def test_auth_forbids_buyer_mock(client):
    headers = {"Authorization": "Bearer buyer:alice"}
    resp = client.post("/api/v1/listings/", json={"title": "X", "price": 10}, headers=headers)
    assert resp.status_code == 403