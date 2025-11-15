from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas, models
from app.services import bookings_service
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.BookingRead, status_code=201)
def create_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
):
    """
    Admin-only primitive for creating bookings directly.

    - Expects buyer_user_id in the payload.
    """
    return crud.create_booking(db, payload)


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
        return crud.list_bookings_for_user(db, user.id)

    #Admin, Org_Admin all get full list - IMPLEMENT LATER
    #return crud.list_bookings(db)


@router.post("/request", response_model=schemas.BookingRead)
def request_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Buyer requests a new booking.

    buyer_user_id is derived from the authenticated user (get_current_user).
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