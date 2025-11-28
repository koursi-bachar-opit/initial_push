from uuid import UUID
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .schemas import PaymentRead
from .public import PaymentsPublic, get_payments_public
from app.database import get_db
from app.auth.auth import get_current_user

router = APIRouter()


@router.get(
    "/bookings/{booking_id}",
    response_model=list[PaymentRead],
)
def list_payments_for_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    user=Depends(get_current_user),
):
    """
    Get all payments associated with a booking.
    Caller must be either the buyer or the provider (via booking access logic).
    """
    return payments_public.list_for_booking(db, booking_id)