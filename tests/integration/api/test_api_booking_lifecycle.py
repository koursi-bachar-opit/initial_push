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
    booking = create_booking(client, db_session)

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
    booking = create_booking(client, db_session)

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