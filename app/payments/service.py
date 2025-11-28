from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session

from .models import Payment, PaymentType, PaymentStatus
from .repository import PaymentsRepository
from .ports.payment_port import PaymentPort
from app.payments.ports.stripe_adapter import get_payment_port

from app.database import get_db
from fastapi import Depends

from app.providers.public import ProvidersPublic, get_providers_public  #NEW LINE

#consider:
#Future extension:
#def reconcile(self, db: Session, *, event_payload: dict): ...
#For Stripe webhooks
class PaymentsService:
    """
    Orchestrates payment flows:
    - Escrow creation (authorization hold)
    - Capture (final charge)
    - Refund (void or refund)
    This service:
    - Enforces booking lifecycle rules
    - Coordinates with the payment processor via PaymentPort
    - Persists Payment records using PaymentRepository
    - Does NOT import booking models or repositories directly
    """
    def __init__(
        self,
        repo: PaymentsRepository,
        port: PaymentPort,
        providers_public: ProvidersPublic,  #NEW LINE
    ):
        self.repo = repo
        self.port = port
        self.providers_public = providers_public  #NEW LINE


    #Escrow (auth hold)
    def create_escrow(
        self,
        db: Session,
        *,
        booking,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        """
        Creates an authorization/escrow hold for a booking.
        Called after booking confirmation.
        """
        processor_ref = self.port.create_hold(
            amount=amount,
            currency=currency,
            reference=str(booking.id),
        )

        payment = Payment(
            booking_id=booking.id,
            type=PaymentType.ESCROW,
            amount=amount,
            currency=currency,
            processor_ref=processor_ref,
            status=PaymentStatus.AUTHORIZED,
        )

        return self.repo.create_payment(db, payment)


    #Final charge
    def capture(self, db: Session, *, booking) -> Payment:
        """
        Capture the authorized escrow created earlier.
        Called when a booking is completed.
        """
        escrow = self.repo.get_latest_escrow(db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to capture.") #TODO: convert to domain error

        if escrow.status != PaymentStatus.AUTHORIZED:
            raise ValueError("Escrow already captured or refunded.")    #TODO: convert to domain error

        #capture via port
        self.port.capture(processor_ref=escrow.processor_ref)

        #update local payment state
        escrow.status = PaymentStatus.CAPTURED
        return self.repo.update_payment(db, escrow)

    #cancel booking -> return escrow
    def void_escrow(
        self,
        db: Session,
        *,
        booking,
    ) -> Payment:
        """
        Void an existing escrow authorization.
        Used when a booking is cancelled before session start.
        Buyers cannot cancel after booking start.
        """
        escrow = self.repo.get_latest_escrow(db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to void.")

        if escrow.status != PaymentStatus.AUTHORIZED:
            raise ValueError("Only an authorized escrow can be voided.")

        #Process void via payment port
        self.port.refund(
            processor_ref=escrow.processor_ref,
            amount=Decimal("0.00"),  #void = cancel auth, not refund
        )

        #Mark escrow as refunded/voided
        escrow.status = PaymentStatus.REFUNDED
        return self.repo.update_payment(db, escrow)

    #Refund call in disputes
    def refund(
        self,
        db: Session,
        *,
        booking,
        reason: str | None = None,
    ) -> Payment:
        """
        Refund an existing escrow or captured payment.
        Void or refund..
        Called when a booking is cancelled.
        """

        #until: if booking is not completed, raise ValueError("Cannot refund payment: booking not completed.")
        escrow = self.repo.get_latest_escrow(db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to refund.") #TODO: convert to domain error

        #Process refund with Stripe (or mock)
        self.port.refund(
            processor_ref=escrow.processor_ref,
            amount=escrow.amount,
        )

        #Record refund
        refund_payment = Payment(
            booking_id=booking.id,
            type=PaymentType.REFUND,
            amount=escrow.amount,
            currency=escrow.currency,
            processor_ref=escrow.processor_ref,
            status=PaymentStatus.REFUNDED,
        )

        return self.repo.create_payment(db, refund_payment)


    #query
    def list_for_booking(self, db: Session, booking):
        return self.repo.list_payments_for_booking(db, booking.id)
    
    def get_payments_for_bookings(self, db: Session, booking_ids: list[UUID]):
        return self.repo.list_payments_for_bookings(db, booking_ids)


def get_payments_service(
    db=Depends(get_db),
    port: PaymentPort = Depends(get_payment_port),
    providers_public: ProvidersPublic = Depends(get_providers_public),  #NEW LINE
) -> PaymentsService:

    repo = PaymentsRepository()

    return PaymentsService(
        repo=repo,
        port=port,
        providers_public=providers_public,  #NEW LINE
    )