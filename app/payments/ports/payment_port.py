from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Protocol, Optional


class PaymentPort(Protocol):
    """
    Complete payment processor interface.
    The PaymentService depends on this abstraction, not on any concrete
    provider (Stripe, PayPal, for example).
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
        raise NotImplementedError

    @abstractmethod
    def capture(
        self,
        *,
        processor_ref: str,
    ) -> None:
        """
        Capture a previously authorized payment.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    # NEW METHODS - Add these based on your actual usage
    
    @abstractmethod
    def create_payment_intent(
        self,
        *,
        amount: Decimal,
        currency: str,
        reference: str,
        capture_method: str = "manual",
    ) -> dict:
        """
        Create a PaymentIntent for frontend Stripe Elements.
        Returns dict with client_secret and payment_intent_id.
        """
        raise NotImplementedError

    @abstractmethod
    def confirm_payment_intent(
        self,
        *,
        payment_intent_id: str,
    ) -> dict:
        """
        Confirm a PaymentIntent after frontend collection.
        """
        raise NotImplementedError

    @abstractmethod
    def get_payment_intent(
        self,
        *,
        payment_intent_id: str,
    ) -> Optional[dict]:
        """
        Retrieve a PaymentIntent status from processor.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_payment_intent(
        self,
        *,
        processor_ref: str,
    ) -> None:
        """
        Cancel a PaymentIntent that won't be used.
        """
        raise NotImplementedError

    # @abstractmethod
    # def cancel_payment_intent(
    #     self,
    #     *,
    #     payment_intent_id: str,
    # ) -> None:
    #     """
    #     Cancel a PaymentIntent that won't be used.
    #     """
    #     raise NotImplementedError


# from abc import ABC, abstractmethod
# from decimal import Decimal
# from typing import Protocol


# class PaymentPort(Protocol):
#     """
#     Abstract payment processor interface.
#     The PaymentService depends on this abstraction, not on any concrete
#     provider (Stripe, PayPal, for example).
#     Responsibilities:
#     - Create an escrow/authorization hold
#     - Capture an existing authorization
#     - Refund a captured or authorized payment
#     """
#     @abstractmethod
#     def create_hold(
#         self,
#         *,
#         amount: Decimal,
#         currency: str,
#         reference: str,
#     ) -> str:
#         """
#         Create an authorization/hold on the user's payment method.
#         Returns a processor reference ID (e.g., Stripe PaymentIntent ID).
#         """
#         raise NotImplementedError   #consider: notimplemented

#     @abstractmethod
#     def capture(
#         self,
#         *,
#         processor_ref: str,
#     ) -> None:
#         """
#         Capture a previously authorized payment.
#         """
#         raise NotImplementedError   #consider: notimplemented

#     @abstractmethod
#     def refund(
#         self,
#         *,
#         processor_ref: str,
#         amount: Decimal,
#     ) -> None:
#         """
#         Refund a previously captured or authorized payment.
#         """
#         raise NotImplementedError   #consider: notimplemented