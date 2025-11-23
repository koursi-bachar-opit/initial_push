from datetime import datetime, timedelta, timezone     # CHANGED: needed to construct safe booking windows per test
from factories.bookings import create_booking
from test_helpers import ApiClient
from assertions import (
    assert_status_code, 
    assert_booking_status, 
    assert_booking_lifecycle_state,
    assert_timestamp_field_exists,
    assert_response_contains
)


def test_full_booking_lifecycle_confirm_cancel(client, db_session):
    """
    Full booking lifecycle: request -> confirm -> cancel
    """
    api = ApiClient(client)

    # For this test we need the booking to be cancellable after confirmation.
    # That means "now" must still be before start_time when cancel is called.
    now = datetime.now(timezone.utc)                           # CHANGED: base time for this scenario
    start = now + timedelta(hours=2)                           # CHANGED: start well in the future so cancel is allowed
    end = start + timedelta(hours=1)                           # CHANGED: 1-hour window after start

    booking = create_booking(
        client,
        db_session,
        start_time=start.isoformat(),                          # CHANGED: override start_time so cancel rule passes
        end_time=end.isoformat(),                              # CHANGED: override end_time consistently
    )

    #Confirm booking
    response = api.put_booking_action(booking['id'], 'confirm', 'admin')
    assert_status_code(response, 200)
    assert_booking_status(response, 'confirmed')

    #Cancel booking  
    response = api.put_booking_action(booking['id'], 'cancel', 'admin')
    assert_status_code(response, 200)
    assert_booking_status(response, 'cancelled')


def test_booking_usage_session_start_and_end(client, db_session):
    """
    confirm -> start -> end
    """
    api = ApiClient(client)

    # For this test we need to be able to start the session immediately.
    # That means "now" must fall between [start_time, end_time].
    now = datetime.now(timezone.utc)                           # CHANGED: base time for this scenario
    start = now - timedelta(minutes=5)                         # CHANGED: start slightly in the past so start_session passes
    end = now + timedelta(hours=1)                             # CHANGED: end in the future to keep window open

    booking = create_booking(
        client,
        db_session,
        start_time=start.isoformat(),                          # CHANGED: override start_time for "in-window" start
        end_time=end.isoformat(),                              # CHANGED: override end_time for "in-window" start
    )

    # Confirm booking
    response = api.put_booking_action(booking['id'], 'confirm', 'admin')
    assert_status_code(response, 200)

    # Start session
    response = api.put_booking_action(booking['id'], 'start', 'provider')
    assert_booking_lifecycle_state(response, 'active', has_active_session=True)

    # End session
    response = api.put_booking_action(booking['id'], 'end', 'provider')
    assert_status_code(response, 200)
    assert_booking_status(response, 'completed')
    assert_response_contains(response, 'usage_seconds')  # Pass response object
    assert_response_contains(response, 'actual_price_charged')  # Pass response object