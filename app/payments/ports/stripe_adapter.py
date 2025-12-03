import os
import uuid
from decimal import Decimal
from typing import Optional
import stripe

from .payment_port import PaymentPort


class RealStripeAdapter(PaymentPort):
    """
    Real Stripe adapter implementing the complete PaymentPort interface.
    """
    
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe.api_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")

    def create_hold(
        self,
        *,
        amount: Decimal,
        currency: str,
        reference: str,
    ) -> str:
        """Create authorization hold - uses create_payment_intent internally"""
        intent_data = self.create_payment_intent(
            amount=amount,
            currency=currency,
            reference=reference,
            capture_method="manual"
        )
        return intent_data["payment_intent_id"]

    def create_payment_intent(
        self,
        *,
        amount: Decimal,
        currency: str,
        reference: str,
        capture_method: str = "manual",
    ) -> dict:
        """Create PaymentIntent for frontend Stripe Elements"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency=currency.lower(),
                capture_method=capture_method,
                metadata={"booking_id": reference},
                payment_method_types=["card"],
            )
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": amount,
                "currency": currency
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    def confirm_payment_intent(
        self,
        *,
        payment_intent_id: str,
    ) -> dict:
        """Confirm PaymentIntent after frontend collection"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            #If you need to confirm server-side
            #intent = stripe.PaymentIntent.confirm(payment_intent_id)
            return {
                "status": intent.status,
                "payment_intent_id": intent.id
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe confirmation error: {str(e)}")

    def get_payment_intent(
        self,
        *,
        payment_intent_id: str,
    ) -> Optional[dict]:
        """Retrieve PaymentIntent status"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": Decimal(intent.amount) / 100,
                "currency": intent.currency,
                "client_secret": intent.client_secret,
                "capture_method": intent.capture_method
            }
        except stripe.error.StripeError:
            return None

    def capture(
        self,
        *,
        processor_ref: str,
    ) -> None:
        """Capture authorized payment"""
        try:
            stripe.PaymentIntent.capture(processor_ref)
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe capture error: {str(e)}")

    def cancel_payment_intent(
        self,
        *,
        processor_ref: str,
    ) -> None:
        """Cancel a payment intent (for uncaptured payments)"""
        try:
            stripe.PaymentIntent.cancel(processor_ref)
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe cancel error: {str(e)}")

    def refund(
        self,
        *,
        processor_ref: str,
        amount: Decimal,
    ) -> None:
        """Refund payment (for captured payments)"""
        try:
            stripe.Refund.create(
                payment_intent=processor_ref,
                amount=int(amount * 100),
            )
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe refund error: {str(e)}")


class MockStripeAdapter(PaymentPort):
    """
    Mock adapter implementing the complete PaymentPort interface.
    """
    def create_hold(self, *, amount, currency, reference) -> str:
        return f"pi_mock_{uuid.uuid4().hex}"

    def create_payment_intent(self, *, amount, currency, reference, capture_method="manual") -> dict:
        payment_intent_id = f"pi_mock_{uuid.uuid4().hex}"
        return {
            "payment_intent_id": payment_intent_id,
            "client_secret": f"cs_mock_{uuid.uuid4().hex}",
            "status": "requires_payment_method",
            "amount": amount,
            "currency": currency
        }

    def confirm_payment_intent(self, *, payment_intent_id) -> dict:
        return {"status": "succeeded", "payment_intent_id": payment_intent_id}

    def get_payment_intent(self, *, payment_intent_id) -> Optional[dict]:
        return {
            "id": payment_intent_id,
            "status": "succeeded",
            "amount": Decimal("100.00"),
            "currency": "usd",
            "client_secret": f"cs_mock_{uuid.uuid4().hex}",
            "capture_method": "manual"
        }

    def capture(self, *, processor_ref) -> None:
        return None

    def refund(self, *, processor_ref, amount) -> None:
        return None
    
    def cancel_payment_intent(self, *, processor_ref) -> None:
        return None


def get_payment_adapter() -> PaymentPort:
    """Factory function returning PaymentPort interface"""
    if os.getenv("USE_REAL_STRIPE", "false").lower() == "true":
        return RealStripeAdapter()
    else:
        return MockStripeAdapter()


# import uuid
# from decimal import Decimal

# from .payment_port import PaymentPort


# class StripeAdapter(PaymentPort):
#     """
#     Mock Stripe adapter.
#     - This adapter generates deterministic mock processor references.
#     - Stripe implementation: Stripe SDK calls
#     This implementation allows your PaymentService to function end-to-end
#     without needing Stripe credentials during development.
#     """

#     def create_hold(
#         self,
#         *,
#         amount: Decimal,
#         currency: str,
#         reference: str,
#     ) -> str:
#         """
#         Create a mock authorization/hold and return a fake PaymentIntent ID.
#         Stripe implementation:
#         stripe.PaymentIntent.create(
#             amount=int(amount * 100),
#             currency=currency,
#             capture_method="manual",
#             metadata={"booking_id": reference},
#         )
#         """
#         #Mock: generate a deterministic fake "pi_" ID
#         return f"pi_{uuid.uuid4().hex}"


#     def capture(
#         self,
#         *,
#         processor_ref: str,
#     ) -> None:
#         """
#         Capture the previously authorized amount.
#         Stripe implementation:
#         stripe.PaymentIntent.capture(processor_ref)
#         """
#         #Mock
#         return None


#     def refund(
#         self,
#         *,
#         processor_ref: str,
#         amount: Decimal,
#     ) -> None:
#         """
#         Refund a previously authorized/captured payment.
#         Stripe implementation:
#         stripe.Refund.create(
#             payment_intent=processor_ref,
#             amount=int(amount * 100),
#         )
#         """
#         #Mock
#         return None
    

# def get_stripe_adapter() -> StripeAdapter:
#     return StripeAdapter()

# # def get_payment_port() -> PaymentPort:
# #     return StripeAdapter()