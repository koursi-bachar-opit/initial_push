from uuid import UUID
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.orm import Session

from .models import Payment, PaymentType, PaymentStatus
from .repository import PaymentsRepository
from .ports.payment_port import PaymentPort

from app.database import get_db
from fastapi import Depends

from app.providers.public import ProvidersPublic, get_providers_public
from app.notifications.public import NotificationsPublic, get_notifications_public
from .ports.stripe_adapter import get_payment_adapter

import stripe


class PaymentsService:
    """
    Orchestrates payment flows:
    - Escrow creation (authorization hold)
    - Capture (final charge)
    - Refund (void or refund)
    """
    def __init__(
        self,
        db: Session,
        repo: PaymentsRepository,
        port: PaymentPort,
        providers_public: ProvidersPublic,
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.repo = repo
        self.port = port
        self.providers_public = providers_public
        self.notifications = notifications_public


    # Escrow (auth hold)
    def create_escrow(
        self,
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

        return self.repo.create_payment(self.db, payment)






    def void_escrow(self, booking) -> Payment:
        """Void escrow - cancel authorization for uncaptured payments"""
        escrow = self.repo.get_latest_escrow(self.db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to void.")
        
        if escrow.status == PaymentStatus.AUTHORIZED:
            # Payment intent exists but not captured - cancel it
            try:
                # Cancel the payment intent in Stripe
                canceled_intent = stripe.PaymentIntent.cancel(escrow.processor_ref)
                
                # Update local status
                escrow.status = PaymentStatus.CANCELLED
                return self.repo.update_payment(self.db, escrow)
            except stripe.error.StripeError as e:
                raise ValueError(f"Failed to void payment: {str(e)}")
        else:
            raise ValueError(f"Cannot void escrow in status: {escrow.status}. Only AUTHORIZED payments can be voided.")

    def capture(self, booking) -> Payment:
        """Capture the authorized escrow created earlier."""
        escrow = self.repo.get_latest_escrow(self.db, booking.id)
        if not escrow:
            raise ValueError("No escrow found to capture.")
        
        if escrow.status != PaymentStatus.AUTHORIZED:
            raise ValueError("Escrow already captured or refunded.")
        
        try:
            # Capture the payment in Stripe
            captured_intent = stripe.PaymentIntent.capture(escrow.processor_ref)
            
            # Update local payment state
            escrow.status = PaymentStatus.CAPTURED
            updated = self.repo.update_payment(self.db, escrow)
            
            self.notifications.payment_captured(booking.buyer, updated)
            
            return updated
        except stripe.error.StripeError as e:
            raise ValueError(f"Failed to capture payment: {str(e)}")

    def refund(self, booking_id, reason: str | None = None) -> Payment:
        """Refund a captured payment."""
        # Get the captured payment (not just any escrow)
        captured_payment = (
            self.db.query(Payment)
            .filter(
                Payment.booking_id == booking_id,
                Payment.type == PaymentType.ESCROW,
                Payment.status == PaymentStatus.CAPTURED
            )
            .first()
        )
        
        if not captured_payment:
            raise ValueError("No captured payment found to refund.")
        
        try:
            # Create refund in Stripe
            refund_obj = stripe.Refund.create(
                payment_intent=captured_payment.processor_ref,
                amount=int(captured_payment.amount * 100),
                reason="requested_by_customer" if reason else None,
            )
            
            # Record refund payment
            refund_payment = Payment(
                booking_id=booking_id,
                type=PaymentType.REFUND,
                amount=captured_payment.amount,
                currency=captured_payment.currency,
                processor_ref=refund_obj.id,
                status=PaymentStatus.REFUNDED,
            )
            
            return self.repo.create_payment(self.db, refund_payment)
        except stripe.error.StripeError as e:
            raise ValueError(f"Failed to refund payment: {str(e)}")

    # # Final charge
    # def capture(self, booking) -> Payment:
    #     """
    #     Capture the authorized escrow created earlier.
    #     Called when a booking is completed.
    #     """
    #     escrow = self.repo.get_latest_escrow(self.db, booking.id)
    #     if not escrow:
    #         raise ValueError("No escrow found to capture.") #TODO: convert to domain error

    #     if escrow.status != PaymentStatus.AUTHORIZED:
    #         raise ValueError("Escrow already captured or refunded.")    #TODO: convert to domain error

    #     #capture via port
    #     self.port.capture(processor_ref=escrow.processor_ref)

    #     #update local payment state
    #     escrow.status = PaymentStatus.CAPTURED
    #     updated = self.repo.update_payment(self.db, escrow)

    #     self.notifications.payment_captured(booking.buyer, updated)

    #     return updated


    # def void_escrow(self, booking) -> Payment:
    #     """Void escrow, cancel payment intent for uncaptured payments"""
    #     escrow = self.repo.get_latest_escrow(self.db, booking.id)
    #     if not escrow:
    #          raise ValueError("No escrow found to void.")
        
    #     if escrow.status == PaymentStatus.AUTHORIZED:
    #         #Payment intent exists but not captured - cancel it
    #         self.port.cancel_payment_intent(
    #             processor_ref=escrow.processor_ref,
    #         )
    #         escrow.status = PaymentStatus.CANCELLED
    #     else:
    #         raise ValueError(f"Cannot void escrow in status: {escrow.status}. Only AUTHORIZED payments can be voided.")
        
    #     return self.repo.update_payment(self.db, escrow)


    # #consider: refund call in disputes
    # #self.notifications.refund_issued(booking.buyer, updated)
    # #now takes booking_id instead of booking
    # def refund(
    #     self,
    #     booking_id,
    #     reason: str | None = None,
    # ) -> Payment:
    #     """
    #     Refund an existing escrow or captured payment.
    #     Void or refund..
    #     Called when a booking is cancelled.
    #     """

    #     #until: if booking is not completed, raise ValueError("Cannot refund payment: booking not completed.")
    #     escrow = self.repo.get_latest_escrow(self.db, booking_id)
    #     if not escrow:
    #         raise ValueError("No escrow found to refund.") #TODO: convert to domain error

    #     #Process refund with Stripe (or mock)
    #     self.port.refund(
    #         processor_ref=escrow.processor_ref,
    #         amount=escrow.amount,
    #     )

    #     #Record refund
    #     refund_payment = Payment(
    #         booking_id=booking_id,
    #         type=PaymentType.REFUND,
    #         amount=escrow.amount,
    #         currency=escrow.currency,
    #         processor_ref=escrow.processor_ref,
    #         status=PaymentStatus.REFUNDED,
    #     )

    #     return self.repo.create_payment(self.db, refund_payment)


    #query
    def list_for_booking(self, booking_id):    #consider: takes booking ID to pass tests, many others still take full object
        return self.repo.list_payments_for_booking(self.db, booking_id)
    
    def get_payments_for_bookings(self, booking_ids: list[UUID]):
        return self.repo.list_payments_for_bookings(self.db, booking_ids)
    

    # UPDATED: Checkout Session methods
    def create_checkout_session(
        self,
        booking_id: UUID,
        user_id: str,  # ADDED: User ID for metadata
        amount: Decimal,
        currency: str,
        success_url: str,
        cancel_url: str,
        customer_email: str = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session for hosted payment page.
        """
        result = self.port.create_checkout_session(
            booking_id=str(booking_id),
            user_id=user_id,  # ADDED: Pass user_id to port
            amount=amount,
            currency=currency,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
        )
        
        # Optional: Create a pending payment record
        # You could store the session reference without a processor_ref yet
        # payment = Payment(
        #     booking_id=booking_id,
        #     type=PaymentType.ESCROW,
        #     amount=amount,
        #     currency=currency,
        #     processor_ref=None,  # Will be filled by webhook
        #     status=PaymentStatus.AUTHORIZED,
        # )
        # self.repo.create_payment(self.db, payment)
        
        return result

    def verify_checkout_session(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Verify a Stripe Checkout Session and get payment details.
        """
        return self.port.retrieve_checkout_session(session_id=session_id)


    def create_payment_intent(
        self,
        booking_id: UUID,
        amount: Decimal,
        currency: str = "USD",
    ) -> dict:
        """
        Create a Stripe PaymentIntent for frontend Stripe Elements.
        Returns client_secret for frontend payment confirmation.
        """
        
        # Create the PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency.lower(),
            capture_method="manual",  # Authorize now, capture later
            metadata={"booking_id": str(booking_id)},
            #For testing - can specify specific payment methods
            payment_method_types=["card"],
        )
        
        # Store the PaymentIntent reference in our database
        payment = Payment(
            booking_id=booking_id,
            type=PaymentType.ESCROW,
            amount=amount,
            currency=currency,
            processor_ref=intent.id,
            status=PaymentStatus.AUTHORIZED,
        )
        self.repo.create_payment(self.db, payment)
        
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": amount,
            "currency": currency
        }


def get_payments_service(
    db: Session = Depends(get_db),
    port: PaymentPort = Depends(get_payment_adapter),
    providers_public: ProvidersPublic = Depends(get_providers_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> PaymentsService:

    repo = PaymentsRepository()

    return PaymentsService(
        db=db,
        repo=repo,
        port=port,
        providers_public=providers_public,
        notifications_public=notifications_public,
    )