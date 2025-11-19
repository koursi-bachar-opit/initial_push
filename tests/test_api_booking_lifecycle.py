from datetime import datetime, timedelta, timezone


def _setup_booking(client):
    #listing helper
    headers = {"Authorization": "Bearer provider:alice@example.com"}
    l = client.post(
        "/api/v1/listings/",
        json={"title": "Lifecycle GPU", "price": 5.0},
        headers=headers,
    )
    listing_id = l.json()["id"]

    #request booking as buyer (window includes "now" for start/end tests)
    now = datetime.now(timezone.utc)
    payload = {
        "listing_id": listing_id,
        "start_time": (now - timedelta(minutes=5)).isoformat(),
        "end_time": (now + timedelta(minutes=5)).isoformat(),
    }
    buyer_headers = {"Authorization": "Bearer buyer:bob@example.com"}
    b = client.post("/api/v1/bookings/request", json=payload, headers=buyer_headers)
    return b.json()["id"]


def test_full_booking_lifecycle_confirm_cancel(client):
    booking_id = _setup_booking(client)

    #confirm
    r = client.put(f"/api/v1/bookings/{booking_id}/confirm")
    assert r.status_code == 200
    assert r.json()["status"] in ("confirmed", "CONFIRMED")

    #cancel
    r = client.put(f"/api/v1/bookings/{booking_id}/cancel")
    assert r.status_code == 200
    assert r.json()["status"] in ("cancelled", "CANCELLED")


def test_booking_usage_session_start_and_end(client):
    booking_id = _setup_booking(client)

    #confirm first
    rc = client.put(f"/api/v1/bookings/{booking_id}/confirm")
    assert rc.status_code == 200

    #start
    rs = client.put(f"/api/v1/bookings/{booking_id}/start")
    assert rs.status_code == 200
    data = rs.json()
    assert data["status"] in ("active", "ACTIVE")
    assert data["active_session_start"] is not None

    #end
    re = client.put(f"/api/v1/bookings/{booking_id}/end")
    assert re.status_code == 200
    data = re.json()
    assert data["status"] in ("completed", "COMPLETED")
    assert data["actual_price_charged"] is not None
    assert data["usage_seconds"] is not None