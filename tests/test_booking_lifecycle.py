import pytest

def test_booking_lifecycle(client):
    # Create a listing
    headers = {"Authorization": "Bearer provider:alice"}
    listing = client.post("/api/v1/listings/", json={"title": "Test Server", "price": 5.0}, headers=headers)
    listing_id = listing.json()["id"]

    # Request booking
    payload = {
        "listing_id": listing_id,
        "buyer_name": "Alice",
        "start_time": "2025-11-10T10:00:00Z",
        "end_time": "2025-11-10T12:00:00Z"
    }
    booking = client.post("/api/v1/bookings/", json=payload)
    assert booking.status_code == 201
    booking_id = booking.json()["id"]

    # Confirm booking
    r = client.put(f"/api/v1/bookings/{booking_id}/confirm")
    assert r.status_code == 200
    assert r.json()["status"] == "confirmed"

    # Cancel booking
    r = client.put(f"/api/v1/bookings/{booking_id}/cancel")
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"