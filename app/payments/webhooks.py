from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from .repository import PaymentsRepository
from .models import PaymentStatus
from .public import get_payments_public, PaymentsPublic
from app.database import get_db
#import stripe
#stripe.Webhook.construct_event(...)



router = APIRouter(prefix="/payments/webhooks", tags=["payments:webhooks"])

#consider, make calls to service, not repo
@router.post("/stripe")
def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    payments_public: PaymentsPublic = Depends(get_payments_public),
):
    """
    Stripe webhook endpoint
    Processes out-of-band events from the payment processor
    """
    try:
        payload = request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event_type = payload.get("type")
    data = payload.get("data", {}).get("object", {})
    processor_ref = data.get("id")

    if not processor_ref:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing processor reference",
        )

    repo = PaymentsRepository()
    payment = repo.get_by_processor_ref(db, processor_ref)
    if not payment:
        return {"status": "ignored", "reason": "payment not found"}

    if event_type == "payment_intent.succeeded":
        if payment.status != PaymentStatus.CAPTURED:
            payment.status = PaymentStatus.CAPTURED
            repo.update_payment(db, payment)
        return {"status": "ok", "updated": "captured"}

    if event_type == "payment_intent.payment_failed":
        payment.status = PaymentStatus.FAILED
        repo.update_payment(db, payment)
        return {"status": "ok", "updated": "failed"}

    return {"status": "ignored", "event": event_type}