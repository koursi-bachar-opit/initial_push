from datetime import datetime, timedelta, timezone
import uuid

import pytest
from fastapi import HTTPException

from app import models, schemas
from app.services import bookings_service
from app.repositories import listing_repository, user_repository


#Helpers
def _create_user(db_session):
    """Create a user with always-unique supabase_id + email."""
    supabase_id = str(uuid.uuid4())
    email = f"user-{uuid.uuid4()}@example.com"
    return user_repository.create_user(
        db_session,
        email=email,
        supabase_id=supabase_id,
        role=models.UserRole.BUYER,
    )


def _create_listing(db_session, price=5.0):
    """Create a listing with minimal required fields."""
    payload = schemas.ListingCreate(title="Service GPU", price=price)
    return listing_repository.create_listing(db_session, payload)



def test_request_booking_computes_price_and_sets_status(db_session):
    """Booking request computes estimate and sets status=REQUESTED."""
    user = _create_user(db_session)
    listing = _create_listing(db_session, price=10.0)

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=3)

    booking = bookings_service.request_booking(
        db=db_session,
        listing_id=listing.id,
        buyer_user_id=user.id,
        start_time=start,
        end_time=end,
    )

    assert booking.listing_id == listing.id
    assert booking.buyer_user_id == user.id
    assert booking.status == models.BookingStatus.REQUESTED
    assert booking.total_price_estimate == pytest.approx(30.0)
    assert booking.start_time == start
    assert booking.end_time == end


def test_confirm_and_cancel_booking_change_status(db_session):
    """Confirm then cancel should produce CONFIRMED → CANCELLED."""
    user = _create_user(db_session)
    listing = _create_listing(db_session, price=5.0)

    now = datetime.now(timezone.utc)

    booking = models.Booking(
        listing_id=listing.id,
        buyer_user_id=user.id,
        start_time=now,
        end_time=now + timedelta(hours=1),
        status=models.BookingStatus.REQUESTED,
        total_price_estimate=5.0,
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    confirmed = bookings_service.confirm_booking(db_session, booking.id)
    assert confirmed.status == models.BookingStatus.CONFIRMED

    cancelled = bookings_service.cancel_booking(db_session, booking.id)
    assert cancelled.status == models.BookingStatus.CANCELLED


def test_start_session_invalid_status_raises(db_session):
    """start_session should fail unless booking is CONFIRMED."""
    user = _create_user(db_session)
    listing = _create_listing(db_session, price=5.0)
    now = datetime.now(timezone.utc)

    booking = models.Booking(
        listing_id=listing.id,
        buyer_user_id=user.id,
        start_time=now - timedelta(minutes=5),
        end_time=now + timedelta(minutes=5),
        status=models.BookingStatus.REQUESTED,  #not confirmed → must fail
        total_price_estimate=5.0,
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    with pytest.raises(HTTPException) as excinfo:
        bookings_service.start_session(db_session, booking.id)

    assert excinfo.value.status_code == 409


def test_start_and_end_session_flow(db_session):
    """Full ACTIVE → COMPLETED flow with usage_seconds + price calculation."""
    user = _create_user(db_session)
    listing = _create_listing(db_session, price=10.0)
    now = datetime.now(timezone.utc)

    booking = models.Booking(
        listing_id=listing.id,
        buyer_user_id=user.id,
        start_time=now - timedelta(minutes=5),
        end_time=now + timedelta(minutes=5),
        status=models.BookingStatus.CONFIRMED,
        total_price_estimate=10.0,
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    #Start session
    started = bookings_service.start_session(db_session, booking.id)
    assert started.status == models.BookingStatus.ACTIVE
    assert started.active_session_start is not None

    #End session
    ended = bookings_service.end_session(db_session, booking.id)
    assert ended.status == models.BookingStatus.COMPLETED
    assert ended.active_session_end is not None
    assert ended.usage_seconds is not None
    assert ended.actual_price_charged is not None
    assert ended.actual_price_charged >= 0