from uuid import UUID
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from .schemas import PaymentRead
from .public import PaymentsPublic, get_payments_public
from app.database import get_db
from app.auth.auth import get_current_user

from .service import PaymentsService, get_payments_service

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


#consider
@router.post("/intent")
def create_payment_intent(
    booking_id: UUID,
    amount: float,
    currency: str = "USD",
    payments_service: PaymentsService = Depends(get_payments_service),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe PaymentIntent for frontend payment collection.
    """
    try:
        from decimal import Decimal
        result = payments_service.create_payment_intent(
            db,
            booking_id=booking_id,
            amount=Decimal(str(amount)),
            currency=currency,
        )
        return result
    except Exception as e:
        raise ValueError(f"Failed to create payment intent: {str(e)}")

@router.get("/{payment_intent_id}/status")
def get_payment_status(
    payment_intent_id: str,
    payments_public: PaymentsPublic = Depends(get_payments_public),
    db: Session = Depends(get_db),
):
    """
    Get payment status for a PaymentIntent.
    """
    # You could check Stripe API here or use your database
    payments = payments_public.list_for_booking(db, payment_intent_id)
    if payments:
        return {"status": payments[0].status}
    return {"status": "unknown"}