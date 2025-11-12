import pytest
from datetime import datetime, timedelta, timezone

@pytest.mark.integration
def test_create_and_read_booking(client):
    headers = {"Authorization": "Bearer provider:alice"}  # <-- add this

    # create a listing first
    resp = client.post("/api/v1/listings/", json={"title": "Test GPU", "price": 15}, headers=headers)
    assert resp.status_code in (200, 201)

    listing_id = resp.json()["id"]

    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(hours=2)

    # create booking (this route is open for buyers)
    headers = {"Authorization": "Bearer buyer:bob"}
    resp = client.post(
        "/api/v1/bookings/",
        json={
            "listing_id": listing_id,
            "buyer_name": "bob",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
        headers=headers,
    )
    assert resp.status_code in (200, 201)

    # verify listing retrieval
    r = client.get("/api/v1/listings/")
    assert any(l["title"] == "Test GPU" for l in r.json())