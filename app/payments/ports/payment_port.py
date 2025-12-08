from abc import abstractmethod
from decimal import Decimal
from typing import Protocol, Optional, Dict, Any


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
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
        """
        Confirm a PaymentIntent after frontend collection.
        """
        raise NotImplementedError

    @abstractmethod
    def get_payment_intent(
        self,
        *,
        payment_intent_id: str,
    ) -> Optional[Dict[str, Any]]:
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

    # UPDATED: Checkout Session method - added user_id parameter
    @abstractmethod
    def create_checkout_session(
        self,
        *,
        booking_id: str,
        user_id: str,  # ADDED: User ID parameter
        amount: Decimal,
        currency: str,
        success_url: str,
        cancel_url: str,
        customer_email: str = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session for hosted payment page.
        Returns dict with session_id and redirect url.
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_checkout_session(
        self,
        *,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve Checkout Session details from processor.
        """
        raise NotImplementedError

# from abc import ABC, abstractmethod
# from decimal import Decimal
# from typing import Protocol, Optional


# class PaymentPort(Protocol):
#     """
#     Complete payment processor interface.
#     The PaymentService depends on this abstraction, not on any concrete
#     provider (Stripe, PayPal, for example).
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
#         raise NotImplementedError

#     @abstractmethod
#     def capture(
#         self,
#         *,
#         processor_ref: str,
#     ) -> None:
#         """
#         Capture a previously authorized payment.
#         """
#         raise NotImplementedError

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
#         raise NotImplementedError

#     # NEW METHODS - Add these based on your actual usage
    
#     @abstractmethod
#     def create_payment_intent(
#         self,
#         *,
#         amount: Decimal,
#         currency: str,
#         reference: str,
#         capture_method: str = "manual",
#     ) -> dict:
#         """
#         Create a PaymentIntent for frontend Stripe Elements.
#         Returns dict with client_secret and payment_intent_id.
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def confirm_payment_intent(
#         self,
#         *,
#         payment_intent_id: str,
#     ) -> dict:
#         """
#         Confirm a PaymentIntent after frontend collection.
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def get_payment_intent(
#         self,
#         *,
#         payment_intent_id: str,
#     ) -> Optional[dict]:
#         """
#         Retrieve a PaymentIntent status from processor.
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def cancel_payment_intent(
#         self,
#         *,
#         processor_ref: str,
#     ) -> None:
#         """
#         Cancel a PaymentIntent that won't be used.
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def create_checkout_session(
#         self,
#         *,
#         booking_id: str,
#         amount: Decimal,
#         currency: str,
#         success_url: str,
#         cancel_url: str,
#         customer_email: str = None,
#     ) -> dict:
#         """
#         Create a Stripe Checkout Session for hosted payment page.
#         Returns dict with session_id and redirect url.
#         """
#         raise NotImplementedError

#     @abstractmethod
#     def retrieve_checkout_session(
#         self,
#         *,
#         session_id: str,
#     ) -> dict:
#         """
#         Retrieve Checkout Session details from processor.
#         """
#         raise NotImplementedError