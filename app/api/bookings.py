from fastapi import APIRouter, Depends, HTTPException

from app import schemas, models
from app.auth.auth import get_current_user
from app.auth.permissions import (
    can_confirm_booking,
    can_cancel_booking,
    can_start_session,
    can_end_session,
)

from app.services.bookings_service import (
    BookingsService,
    get_bookings_service,
)

router = APIRouter()

"""
Routes for managing the booking lifecycle.
Buyers:
    - Can request a booking (`POST /request`)
    - Can see their own bookings
Providers:
    - Can view bookings on their own machines
Admins:
    - Can view all bookings
    - Can create bookings manually
All business logic lives in bookings_service.py.
"""

@router.post("/", response_model=schemas.BookingRead, status_code=201)
def create_booking(
    booking: schemas.BookingAdminCreate,
    user: models.User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Admins sometimes need to create bookings manually 
    (verification checks or manual corrections if not using a PATCH request).
    Regular buyers won't call this route. They use the /request endpoint, 
    which pulls their user id automatically.
    """
    if user.role == models.UserRole.ADMIN:
        try:
            return service.admin_create_booking(payload=booking)
        except ValueError as e: #NotFound -> 404 ValidationError ||| InvalidStateTransition → 400 / 409
            raise HTTPException(status_code=404, detail=str(e)) 
    #explicitly reject non admins
    else:
        raise HTTPException(403)


@router.get("/", response_model=list[schemas.BookingRead])
def list_bookings(
    user: models.User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    #Buyer sees only their own bookings
    if user.role == models.UserRole.BUYER:
        return service.list_bookings_for_user(user.id)

    #Provider sees bookings only for their own machines
    if user.role == models.UserRole.PROVIDER:
        return service.list_bookings_for_provider(user.id)

    # Admins see everything
    if user.role == models.UserRole.ADMIN:
        return service.list_all_bookings()
    
    else:   #Add route for org admins (should see all bookings in their organization only)
        raise HTTPException(403)


@router.post("/request", response_model=schemas.BookingRead)
def request_booking(
    booking: schemas.BookingRequest,
    user: models.User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Buyers don't send their own ID in the request.
    This is configured to trust the authenticated user to decide the buyer identity.
    """
    try:
        return service.request_booking(user.id, payload=booking)
    except ValueError as e: #NotFound -> 404 ValidationError ||| InvalidStateTransition → 400 / 409
        raise HTTPException(status_code=404, detail=str(e))


"""
Represents Booking status values (through bookings_service calls)
confirm_booking() -> CONFIRMED
cancel_booking() -> CANCELLED
start_booking_session() -> ACTIVE
end_booking_session() -> COMPLETED
"""
@router.put("/{booking_id}/confirm", response_model=schemas.BookingRead)
def confirm_booking(booking_id: int, service: BookingsService = Depends(get_bookings_service), user: models.User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

    if can_confirm_booking(user, booking):
        return service.confirm_booking(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id}/cancel", response_model=schemas.BookingRead)
def cancel_booking(booking_id: int, service: BookingsService = Depends(get_bookings_service), user: models.User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_cancel_booking(user, booking):
        return service.cancel_booking(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id}/start", response_model=schemas.BookingRead)
def start_booking_session(booking_id: int, service: BookingsService = Depends(get_bookings_service), user: models.User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_start_session(user, booking):
        return service.start_session(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id}/end", response_model=schemas.BookingRead)
def end_booking_session(booking_id: int, service: BookingsService = Depends(get_bookings_service), user: models.User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_end_session(user, booking):
        return service.end_session(booking_id, booking=booking)
    else:
        raise HTTPException(403)