import pytest

def test_listing_rejects_blank_title_and_negative_price(client):
    headers = {"Authorization": "Bearer provider:alice"}
    resp = client.post(
        "/api/v1/listings/",
        json={"title": "", "price": -10},
        headers=headers,
    )
    assert resp.status_code == 422  # FastAPI validation error