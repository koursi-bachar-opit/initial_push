from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.repositories import booking_repository, listing_repository
from app import schemas
from app import models


def _make_user(db_session, user_id=123):
    """
    Create a valid user that satisfies the NOT NULL constraints
    in models.User:
    - supabase_id (required)
    - email (required)
    - role (required)
    """
    u = models.User(
        id=user_id,
        supabase_id=f"test-supabase-{user_id}",
        email=f"user{user_id}@example.com",
        role=models.UserRole.BUYER,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def _make_listing(db_session):
    payload = schemas.ListingCreate(title="Repo Booking GPU", price=10)
    return listing_repository.create_listing(db_session, payload)


def test_booking_repository_create_and_list(db_session):
    #Create valid user and listing
    _make_user(db_session, 123)
    listing = _make_listing(db_session)

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)

    payload = schemas.BookingCreate(
        listing_id=listing.id,
        start_time=start,
        end_time=end,
        buyer_user_id=123,
    )

    booking = booking_repository.create_booking(db_session, payload)

    #Assertions
    assert booking.id is not None
    assert booking.listing_id == listing.id
    assert booking.buyer_user_id == 123

    #Price calculation: 2 hours * 10 dollars/hour = 20
    assert booking.total_price_estimate == 20

    #list_bookings
    all_bookings = booking_repository.list_bookings(db_session)
    assert any(b.id == booking.id for b in all_bookings)

    #list_bookings_for_user
    user_bookings = booking_repository.list_bookings_for_user(db_session, 123)
    assert len(user_bookings) == 1
    assert user_bookings[0].id == booking.id

    #get_booking_by_id
    fetched = booking_repository.get_booking_by_id(db_session, booking.id)
    assert fetched is not None
    assert fetched.id == booking.id


def test_booking_repository_create_fails_for_missing_listing(db_session):
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)

    payload = schemas.BookingCreate(
        listing_id=999999,   #intentional test number
        start_time=start,
        end_time=end,
        buyer_user_id=123,
    )

    with pytest.raises(HTTPException) as excinfo:
        booking_repository.create_booking(db_session, payload)

    assert excinfo.value.status_code == 404
    assert "Listing not found" in excinfo.value.detail