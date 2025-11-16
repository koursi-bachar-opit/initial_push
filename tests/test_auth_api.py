import pytest
from app import auth

def test_auth_blocks_missing_token_on_protected_endpoint(client):
    #listings POST requires provider/admin role via require_roles
    resp = client.post("/api/v1/listings/", json={"title": "X", "price": 10})
    assert resp.status_code == 401


def test_auth_allows_provider_mock_token(client):
    headers = {"Authorization": "Bearer provider:alice@example.com"}
    resp = client.post("/api/v1/listings/", json={"title": "Mocked Listing", "price": 20}, headers=headers)
    #201 on create
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Mocked Listing"
    assert body["price"] == 20


def test_auth_forbids_buyer_on_provider_only_endpoint(client):
    headers = {"Authorization": "Bearer buyer:bob@example.com"}
    resp = client.post("/api/v1/listings/", json={"title": "X", "price": 10}, headers=headers)
    #require_roles(PROVIDER, ADMIN) should reject a buyer
    assert resp.status_code == 403


def test_auth_cookie_token(client, monkeypatch):
    monkeypatch.setattr("app.auth.settings.SUPABASE_JWT_SECRET", "TESTSECRET")

    import jwt
    token = jwt.encode(
        {"sub": "999", "email": "cookie@example.com", "user_metadata": {"role": "buyer"}},
        "TESTSECRET",
        algorithm="HS256"
    )

    #Set cookie on the client, not per request
    client.cookies.set("access_token", token)

    resp = client.get("/api/v1/bookings/")

    #Allow either 200 or 404 depending on DB state — but NOT 401
    assert resp.status_code in (200, 404)

def test_auth_invalid_jwt_shape(client):
    headers = {"Authorization": "Bearer abc.def"}
    resp = client.get("/api/v1/bookings/", headers=headers)
    assert resp.status_code == 401