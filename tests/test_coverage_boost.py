import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from app import auth
from app.database import get_db
from app.services import bookings_service

# AUTH edge cases
def test_parse_mock_token_bad_format():
    with pytest.raises(HTTPException):
        auth._parse_mock_token("badtoken")

def test_parse_mock_token_wrong_role():
    with pytest.raises(HTTPException):
        auth._parse_mock_token("guest:user")

# DATABASE generator lifecycle
def test_get_db_generator_closes():
    gen = get_db()
    db = next(gen)
    assert db is not None
    with pytest.raises(StopIteration):
        next(gen)


# BOOKINGS API failures
def test_confirm_and_cancel_nonexistent(client):
    r1 = client.put("/api/v1/bookings/9999/confirm")
    r2 = client.put("/api/v1/bookings/9999/cancel")
    assert r1.status_code == 404 and r2.status_code == 404

def test_request_booking_listing_not_found(client):
    now = datetime.now(timezone.utc)
    data = {
        "listing_id": 99999,
        "buyer_name": "ghost",
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(hours=1)).isoformat(),
    }
    r = client.post("/api/v1/bookings/request", json=data)
    assert r.status_code == 404


# BOOKINGS service edge paths
def test_start_and_end_nonexistent(db_session):
    with pytest.raises(HTTPException):
        bookings_service.start_session(db_session, 999)
    with pytest.raises(HTTPException):
        bookings_service.end_session(db_session, 999)

def test_start_session_before_window(db_session, client):
    # build listing & booking normally
    h = {"Authorization": "Bearer provider:alice"}
    l = client.post("/api/v1/listings/", json={"title": "early", "price": 5}, headers=h)
    listing_id = l.json()["id"]
    buyer_headers = {"Authorization": "Bearer buyer:bob"}
    start = datetime.now(timezone.utc) + timedelta(hours=2)
    end = start + timedelta(hours=1)
    b = client.post(
        "/api/v1/bookings/",
        json={"listing_id": listing_id, "buyer_name": "bob",
              "start_time": start.isoformat(), "end_time": end.isoformat()},
        headers=buyer_headers,
    )
    bid = b.json()["id"]
    r = client.put(f"/api/v1/bookings/{bid}/confirm")
    assert r.status_code == 200
    # now start should fail
    r = client.put(f"/api/v1/bookings/{bid}/start")
    assert r.status_code == 400