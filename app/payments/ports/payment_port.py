from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Protocol


class PaymentPort(Protocol):
    """
    Abstract payment processor interface.
    The PaymentService depends on this abstraction, not on any concrete
    provider (Stripe, PayPal, for example).
    Responsibilities:
    - Create an escrow/authorization hold
    - Capture an existing authorization
    - Refund a captured or authorized payment
    """
    @abstractmethod
    def create_hold(
        self,
        *,
        amount: Decimal,
        currency: str,
        reference: str,
    ) -> str:
        """
        Create an authorization/hold on the user's payment method.
        Returns a processor reference ID (e.g., Stripe PaymentIntent ID).
        """
        raise NotImplementedError   #consider: notimplemented

    @abstractmethod
    def capture(
        self,
        *,
        processor_ref: str,
    ) -> None:
        """
        Capture a previously authorized payment.
        """
        raise NotImplementedError   #consider: notimplemented

    @abstractmethod
    def refund(
        self,
        *,
        processor_ref: str,
        amount: Decimal,
    ) -> None:
        """
        Refund a previously captured or authorized payment.
        """
        raise NotImplementedError   #consider: notimplemented