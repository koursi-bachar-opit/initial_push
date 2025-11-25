from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.auth.auth import get_current_user
from app.auth.public import get_auth_public, AuthPublic

from .service import AccessCredentialService, get_access_credential_service
from app.bookings.public import BookingsPublic, get_bookings_public


router = APIRouter()


#Buyer endpoint to fetch credentials for their own active booking
@router.get("/buyer/{booking_id}")
def get_buyer_credentials(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: AccessCredentialService = Depends(get_access_credential_service),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
):
    auth.ensure_buyer(user) #Ensures the user is a buyer

    booking = bookings_public.get_booking(booking_id)

    #Ensure ownership
    if booking.buyer_user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this booking.",
        )

    #service will decide whether credentials should be shown
    creds = service.get_for_booking(booking_id)
    return {"credentials": creds}


#Provider endpoint to fetch credentials for bookings on their machine
@router.get("/provider/{booking_id}")
def get_provider_credentials(
    booking_id: UUID,
    user = Depends(get_current_user),
    auth: AuthPublic = Depends(get_auth_public),
    service: AccessCredentialService = Depends(get_access_credential_service),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
):
    auth.ensure_provider(user)  #Ensures the user is a provider

    booking = bookings_public.get_booking(booking_id)

    #Provider owns the machine
    machine_owner_id = booking.listing.machine.provider_id
    if user.id != machine_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the provider of this machine.",
        )

    creds = service.get_for_booking(booking_id)
    return {"credentials": creds}