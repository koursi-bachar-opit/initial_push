import uuid
from decimal import Decimal

from .payment_port import PaymentPort


class StripeAdapter(PaymentPort):
    """
    Mock Stripe adapter.
    - This adapter generates deterministic mock processor references.
    - Stripe implementation: Stripe SDK calls
    This implementation allows your PaymentService to function end-to-end
    without needing Stripe credentials during development.
    """

    def create_hold(
        self,
        *,
        amount: Decimal,
        currency: str,
        reference: str,
    ) -> str:
        """
        Create a mock authorization/hold and return a fake PaymentIntent ID.
        Stripe implementation:
        stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            capture_method="manual",
            metadata={"booking_id": reference},
        )
        """
        #Mock: generate a deterministic fake "pi_" ID
        return f"pi_{uuid.uuid4().hex}"


    def capture(
        self,
        *,
        processor_ref: str,
    ) -> None:
        """
        Capture the previously authorized amount.
        Stripe implementation:
        stripe.PaymentIntent.capture(processor_ref)
        """
        #Mock
        return None


    def refund(
        self,
        *,
        processor_ref: str,
        amount: Decimal,
    ) -> None:
        """
        Refund a previously authorized/captured payment.
        Stripe implementation:
        stripe.Refund.create(
            payment_intent=processor_ref,
            amount=int(amount * 100),
        )
        """
        #Mock
        return None
    

def get_payment_port() -> PaymentPort:
    return StripeAdapter()