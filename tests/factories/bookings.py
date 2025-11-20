from datetime import datetime, timedelta, timezone
from factories.users import create_user_by_role, auth_headers_by_role
from factories.listings import create_listing
from test_config import TestConfig

def booking_payload(listing_id, buyer_user_id=None, **overrides):
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)

    base = {
        "listing_id": listing_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }

    if buyer_user_id is not None:
        base["buyer_user_id"] = buyer_user_id

    base.update(overrides)
    return base


def create_booking(client, db_session, buyer_role="buyer", provider_role="provider", **overrides):
    buyer = create_user_by_role(db_session, buyer_role)
    listing = create_listing(client, db_session, provider_role=provider_role)

    payload = booking_payload(listing["id"], **overrides)

    resp = client.post(
        "/api/v1/bookings/request",
        json=payload,
        headers=auth_headers_by_role(buyer_role),
    )
    assert resp.status_code == 200
    return resp.json()


def create_booking_for_listing(client, db_session, listing_id, buyer_role="buyer", **overrides):
    """Create a booking for an existing listing."""
    buyer = create_user_by_role(db_session, buyer_role)
    
    payload = booking_payload(listing_id, **overrides)

    resp = client.post(
        "/api/v1/bookings/request",
        json=payload,
        headers=auth_headers_by_role(buyer_role),
    )
    assert resp.status_code == 200
    return resp.json()


def create_booking_direct(client, db_session, listing_payload_overrides=None, booking_payload_overrides=None):
    """Create booking with custom listing and booking parameters."""
    listing_overrides = listing_payload_overrides or {}
    booking_overrides = booking_payload_overrides or {}
    
    return create_booking(
        client,
        db_session,
        **booking_overrides
    )