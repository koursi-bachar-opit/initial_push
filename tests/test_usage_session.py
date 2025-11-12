import pytest
from datetime import datetime, timedelta, timezone

def test_usage_session_start_end_flow(client):
    # create listing (provider token for your auth guard if required)
    headers = {"Authorization": "Bearer provider:alice"}
    r = client.post("/api/v1/listings/", json={"title": "GPU Node", "price": 10.0}, headers=headers)
    assert r.status_code in (200, 201)
    listing_id = r.json()["id"]

    # create booking (existing route)
    now = datetime.now(timezone.utc)
    payload = {
        "listing_id": listing_id,
        "buyer_name": "bob",
        "start_time": (now - timedelta(hours=1)).isoformat(),
        "end_time":   (now + timedelta(hours=1)).isoformat(),
}
    r = client.post("/api/v1/bookings/", json=payload)
    assert r.status_code in (200, 201)
    booking_id = r.json()["id"]

    # confirm booking
    r = client.put(f"/api/v1/bookings/{booking_id}/confirm")
    assert r.status_code in (200, 201)
    assert r.json()["status"] in ("confirmed", "CONFIRMED")

    # start session
    r = client.put(f"/api/v1/bookings/{booking_id}/start")
    assert r.status_code == 200
    data = r.json()
    # sanity check: session start should be recorded
    assert data["status"] in ("active", "ACTIVE")
    assert data["active_session_start"] is not None

    # end session
    r = client.put(f"/api/v1/bookings/{booking_id}/end")
    assert r.status_code == 200
    data = r.json()

    # status and billing verification
    assert data["status"] in ("completed", "COMPLETED")
    assert data["actual_price_charged"] is not None
    assert "usage_seconds" in data
    assert isinstance(data["usage_seconds"], (int, float))
    assert data["usage_seconds"] >= 0
    assert data["actual_price_charged"] >= 0