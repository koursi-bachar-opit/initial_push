from datetime import datetime, timedelta, timezone   # CHANGED: imported for tests that may need explicit time windows
from factories.users import create_user_by_role, auth_headers_by_role
from factories.listings import create_listing
from test_config import TestConfig


def booking_payload(listing_id, buyer_user_id=None, **overrides):
    # Default window: now -> now + 1h, but can be overridden by tests via **overrides
    start = datetime.now(timezone.utc)               # CHANGED: kept as default, tests override when they need custom windows
    end = start + timedelta(hours=1)

    base = {
        "listing_id": listing_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }

    if buyer_user_id is not None:
        base["buyer_user_id"] = buyer_user_id

    # Allow tests to override start_time/end_time/etc explicitly
    base.update(overrides)                           # CHANGED: emphasize that overrides can replace start/end
    return base


def create_booking(client, db_session, buyer_role="buyer", provider_role="provider", **overrides):
    buyer = create_user_by_role(db_session, buyer_role)
    listing = create_listing(client, db_session, provider_role=provider_role)

    # Tests can pass custom start_time/end_time via overrides to satisfy business rules
    payload = booking_payload(listing["id"], **overrides)   # CHANGED: pass overrides down (including custom times)

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
    
    # Same override mechanism here, for consistency with create_booking
    payload = booking_payload(listing_id, **overrides)      # CHANGED: pass overrides for custom windows

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
    
    # Keep behavior the same: booking_overrides still flow into booking_payload via create_booking
    return create_booking(
        client,
        db_session,
        **booking_overrides                              # CHANGED: explicit that these may include custom start/end
    )