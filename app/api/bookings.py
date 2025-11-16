from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas, models
from app.services import bookings_service
from app.auth import get_current_user

router = APIRouter()

"""
Routes for managing the booking lifecycle.
Buyers:
  - Can request a booking (`POST /request`)
  - Can see their own bookings
Admins/Providers:
  - Can view bookings
Admins:
  - Can create bookings manually
All business logic lives in bookings_service.py.
"""

@router.post("/", response_model=schemas.BookingRead, status_code=201)
def create_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Admins sometimes need to create bookings manually 
    (verification checks or manual corrections if not using a PATCH request).
    Regular buyers won't call this route. They use the /request endpoint, 
    which pulls their user id automatically.
    """
    try:
        return bookings_service.admin_create_booking(db, payload)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[schemas.BookingRead])
def list_bookings(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    List bookings visible to the current user.

    - BUYER: only bookings where buyer_user_id == current user's id.
    - PROVIDER: all bookings (until provider scoping is added).
    - ADMIN / ORG_ADMIN: all bookings.
    """
    if user.role == models.UserRole.BUYER:
        return bookings_service.list_bookings_for_user(db, user.id)

    """
    Eventually providers will only see bookings related to their listings
    when connected to buyers by the remote server Machine object. For first testing,
    we allow them to see all bookings for simplicity.
    """
    return bookings_service.list_all_bookings(db)


@router.post("/request", response_model=schemas.BookingRead)
def request_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Buyers don't send their own ID in the request.
    This is configured to trust the authenticated user to decide the buyer identity.
    """
    try:
        return bookings_service.request_booking(
            db=db,
            listing_id=payload.listing_id,
            buyer_user_id=user.id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


"""
Represents Booking status values (through bookings_service calls)
confirm_booking() -> CONFIRMED
cancel_booking() -> CANCELLED
start_booking_session() -> ACTIVE
end_booking_session() -> COMPLETED
"""
@router.put("/{booking_id}/confirm", response_model=schemas.BookingRead)
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    try:
        return bookings_service.confirm_booking(db, booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{booking_id}/cancel", response_model=schemas.BookingRead)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    try:
        return bookings_service.cancel_booking(db, booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{booking_id}/start", response_model=schemas.BookingRead)
def start_booking_session(booking_id: int, db: Session = Depends(get_db)):
    try:
        return bookings_service.start_session(db, booking_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{booking_id}/end", response_model=schemas.BookingRead)
def end_booking_session(booking_id: int, db: Session = Depends(get_db)):
    try:
        return bookings_service.end_session(db, booking_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))