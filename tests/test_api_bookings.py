from datetime import datetime, timedelta, timezone
from app.repositories import user_repository
from app.models import UserRole

def _create_listing_via_api(client):
    #Helper
    headers = {"Authorization": "Bearer provider:alice@example.com"}
    resp = client.post(
        "/api/v1/listings/",
        json={"title": "Booking API GPU", "price": 10},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_admin_create_booking_endpoint(client, db_session):
    #Create the admin user first
    admin_user = user_repository.create_user(
        db=db_session,
        supabase_id="root@example.com",
        email="root@example.com",
        role=UserRole.ADMIN,
    )

    #create listing
    listing_id = _create_listing_via_api(client)

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)

    headers = {"Authorization": "Bearer admin:root@example.com"}
    buyer = user_repository.create_user(
        db=db_session,
        supabase_id="buyer1@example.com",
        email="buyer1@example.com",
        role=UserRole.BUYER,
    )

    payload = {
        "listing_id": listing_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "buyer_user_id": buyer.id,
    }

    resp = client.post("/api/v1/bookings/", json=payload, headers=headers)
    assert resp.status_code == 201


def test_request_booking_and_list_for_buyer_and_provider(client):
    listing_id = _create_listing_via_api(client)

    now = datetime.now(timezone.utc)
    payload = {
        "listing_id": listing_id,
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        #buyer_user_id omitted on purpose, derived from auth user
    }

    #request booking as buyer
    buyer_headers = {"Authorization": "Bearer buyer:bob@example.com"}
    r = client.post("/api/v1/bookings/request", json=payload, headers=buyer_headers)
    assert r.status_code == 200
    booking = r.json()
    booking_id = booking["id"]

    #buyer listing: should see their booking
    rb = client.get("/api/v1/bookings/", headers=buyer_headers)
    assert rb.status_code == 200
    buyer_bookings = rb.json()
    assert any(b["id"] == booking_id for b in buyer_bookings)

    #provider listing: should see all bookings
    provider_headers = {"Authorization": "Bearer provider:alice@example.com"}
    rp = client.get("/api/v1/bookings/", headers=provider_headers)
    assert rp.status_code == 200
    provider_bookings = rp.json()
    assert any(b["id"] == booking_id for b in provider_bookings)