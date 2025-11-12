from datetime import datetime, timedelta, timezone
import pytest

def test_booking_fails_when_end_before_start(client):
    headers = {"Authorization": "Bearer provider:alice"}
    listing = client.post("/api/v1/listings/", json={"title":"T","price":5}, headers=headers)
    listing_id = listing.json()["id"]

    start = datetime.now(timezone.utc)
    end = start - timedelta(hours=1)
    bad_booking = {
        "listing_id": listing_id,
        "buyer_name": "bob",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }
    buyer_headers = {"Authorization": "Bearer buyer:bob"}
    r = client.post("/api/v1/bookings/", json=bad_booking, headers=buyer_headers)
    assert r.status_code in (400, 422)