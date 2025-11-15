from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.services import bookings_service
from app.auth import get_current_user

# Create a router instance to define booking-related API endpoints
router = APIRouter()


# BASIC CRUD ENDPOINTS
@router.post("/", response_model=schemas.BookingRead, status_code=201)
def create_booking(payload: schemas.BookingCreate, db: Session = Depends(get_db)):
    """
    Create a new booking directly (basic CRUD version).
    This is usually used for quick insertion during testing or admin tasks.
    """
    return crud.create_booking(db, payload)

@router.get("/", response_model=list[schemas.BookingRead])
def list_bookings(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    if user.role == models.UserRole.BUYER:
        return db.query(models.Booking).filter_by(buyer_name=user.email).all()

    if user.role == models.UserRole.PROVIDER:
        return (
            db.query(models.Booking)
            .join(models.Listing, models.Booking.listing_id == models.Listing.id)
            .filter(models.Listing.owner_id == user.id)
            .all()
        )

    # admin fallback
    return crud.list_bookings(db)


# FEATURE ENDPOINTS
@router.post("/request", response_model=schemas.BookingRead)
def request_booking(payload: schemas.BookingCreate, db: Session = Depends(get_db)):
    """
    Buyer requests a new booking for a specific listing.
    This endpoint validates the listing, buyer, and time window before saving.
    """
    try:
        return bookings_service.request_booking(
            db=db,
            listing_id=payload.listing_id,
            buyer_name=payload.buyer_name,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
    except ValueError as e:
        # Booking could not be created (e.g., listing not found)
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{booking_id}/confirm", response_model=schemas.BookingRead)
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Provider confirms a pending booking.
    Once confirmed, the booking can be commenced (with delay) by the provider.
    """
    try:
        return bookings_service.confirm_booking(db, booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{booking_id}/cancel", response_model=schemas.BookingRead)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Buyer or provider cancels an existing booking.
    Can only be done before an active session begins.
    """
    try:
        return bookings_service.cancel_booking(db, booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# SESSION MANAGEMENT ENDPOINTS
@router.put("/{booking_id}/start", response_model=schemas.BookingRead)
def start_booking_session(booking_id: int, db: Session = Depends(get_db)):
    """
    Provider starts the active session for a confirmed booking.
    Updates the status to ACTIVE and records the start time.
    """
    try:
        return bookings_service.start_session(db, booking_id)
    except HTTPException:
        # Allow service-level HTTPExceptions to bubble up unchanged
        raise
    except Exception as e:
        # Unexpected errors
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{booking_id}/end", response_model=schemas.BookingRead)
def end_booking_session(booking_id: int, db: Session = Depends(get_db)):
    """
    Provider ends the active session and finalizes billing.
    Calculates total usage time and price, and marks booking as COMPLETED.
    """
    try:
        return bookings_service.end_session(db, booking_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))