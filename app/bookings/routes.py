from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth import get_current_user
from .permissions import (
    can_confirm_booking,
    can_cancel_booking,
    can_start_session,
    can_end_session,
)

from .schemas import (
    BookingRead,
    BookingRequest,
    BookingAdminCreate,
)
from .service import (
    BookingsService,
    get_bookings_service,
)
from app.users.models import User, UserRole  #until users domain migration

from uuid import UUID

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

@router.post("/", response_model=BookingRead, status_code=201)
def create_booking(
    booking: BookingAdminCreate,
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Admins use this to create bookings manually 
    Regular buyers will use use the /request endpoint, 
    which pulls their user id automatically.
    """
    if user.role == UserRole.ADMIN:
        try:
            return service.admin_create_booking(payload=booking)
        except ValueError as e: #NotFound -> 404 ValidationError ||| InvalidStateTransition → 400 / 409
            raise HTTPException(status_code=404, detail=str(e)) 
    #explicitly reject non admins
    else:
        raise HTTPException(403)


@router.get("/", response_model=list[BookingRead])  #actor_user_id=user.id
def list_bookings(
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    #Buyer sees only their own bookings
    if user.role == UserRole.BUYER:
        return service.list_bookings_for_user(user.id)

    #Provider sees bookings only for their own machines
    if user.role == UserRole.PROVIDER:
        return service.list_bookings_for_provider(user.id)

    #Admins see everything
    if user.role == UserRole.ADMIN:
        return service.list_all_bookings()
    
    else:   #Add route for org admins (should see all bookings in their ORGANIZATION only)
        raise HTTPException(403)


@router.post("/request", response_model=BookingRead)
def request_booking(
    booking: BookingRequest,
    user: User = Depends(get_current_user),
    service: BookingsService = Depends(get_bookings_service),
):
    """
    Buyers don't send their own ID in the request.
    Verify the authenticated user to decide the buyer identity.
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
@router.put("/{booking_id:uuid}/confirm", response_model=BookingRead)
def confirm_booking(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

    if can_confirm_booking(user, booking):
        return service.confirm_booking(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id:uuid}/cancel", response_model=BookingRead)
def cancel_booking(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_cancel_booking(user, booking):
        return service.cancel_booking(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id:uuid}/start", response_model=BookingRead)
def start_booking_session(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_start_session(user, booking):
        return service.start_session(booking_id, booking=booking)
    else:
        raise HTTPException(403)


@router.put("/{booking_id:uuid}/end", response_model=BookingRead)
def end_booking_session(booking_id: UUID, service: BookingsService = Depends(get_bookings_service), user: User = Depends(get_current_user)):
    try:
        booking = service.get_booking_readonly(booking_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    if can_end_session(user, booking):
        return service.end_session(booking_id, booking=booking)
    else:
        raise HTTPException(403)