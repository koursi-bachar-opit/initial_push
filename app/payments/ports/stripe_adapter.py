import os
import uuid
from decimal import Decimal
from typing import Optional, Dict, Any
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
    ) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
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
    ) -> Optional[Dict[str, Any]]:
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

    # UPDATED: Checkout Session method - added user_id parameter
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
        """Create Stripe Checkout Session for hosted payment page"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Server Booking #{booking_id}',
                            'description': 'Remote server rental booking',
                        },
                        'unit_amount': int(amount * 100),  # Cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=booking_id,
                customer_email=customer_email,
                metadata={  # UPDATED: Include both booking_id and user_id
                    'booking_id': booking_id,
                    'user_id': user_id,  # ADDED: Store user_id in metadata
                }
            )
            return {
                'session_id': session.id,
                'url': session.url,
                'payment_intent_id': session.payment_intent,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe Checkout error: {str(e)}")

    def retrieve_checkout_session(
        self,
        *,
        session_id: str,
    ) -> Dict[str, Any]:
        """Retrieve Checkout Session details"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'id': session.id,
                'payment_status': session.payment_status,
                'payment_intent': session.payment_intent,
                'customer_email': session.customer_email,
                'amount_total': Decimal(session.amount_total) / 100 if session.amount_total else None,
                'currency': session.currency,
                'metadata': session.metadata,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe retrieval error: {str(e)}")


class MockStripeAdapter(PaymentPort):
    """
    Mock adapter implementing the complete PaymentPort interface.
    """
    def create_hold(self, *, amount, currency, reference) -> str:
        return f"pi_mock_{uuid.uuid4().hex}"

    def create_payment_intent(self, *, amount, currency, reference, capture_method="manual") -> Dict[str, Any]:
        payment_intent_id = f"pi_mock_{uuid.uuid4().hex}"
        return {
            "payment_intent_id": payment_intent_id,
            "client_secret": f"cs_mock_{uuid.uuid4().hex}",
            "status": "requires_payment_method",
            "amount": amount,
            "currency": currency
        }

    def confirm_payment_intent(self, *, payment_intent_id) -> Dict[str, Any]:
        return {"status": "succeeded", "payment_intent_id": payment_intent_id}

    def get_payment_intent(self, *, payment_intent_id) -> Optional[Dict[str, Any]]:
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

    # UPDATED: Mock Checkout Session method - added user_id parameter
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
        """Mock Checkout Session creation"""
        mock_session_id = f"cs_mock_{uuid.uuid4().hex}"
        mock_url = f"https://checkout.stripe.com/pay/{mock_session_id}"
        
        return {
            'session_id': mock_session_id,
            'url': mock_url,
            'payment_intent_id': f"pi_mock_{uuid.uuid4().hex}",
        }

    def retrieve_checkout_session(
        self,
        *,
        session_id: str,
    ) -> Dict[str, Any]:
        """Mock Checkout Session retrieval"""
        return {
            'id': session_id,
            'payment_status': 'paid',
            'payment_intent': f"pi_mock_{uuid.uuid4().hex}",
            'customer_email': 'test@example.com',
            'amount_total': Decimal("100.00"),
            'currency': 'usd',
            'metadata': {'booking_id': 'mock_booking_id', 'user_id': 'mock_user_id'},  # UPDATED
        }


def get_payment_adapter() -> PaymentPort:
    """Factory function returning PaymentPort interface"""
    if os.getenv("USE_REAL_STRIPE", "false").lower() == "true":
        return RealStripeAdapter()
    else:
        return MockStripeAdapter()

# import os
# import uuid
# from decimal import Decimal
# from typing import Optional
# import stripe

# from .payment_port import PaymentPort

# from typing import Dict, Any


# class RealStripeAdapter(PaymentPort):
#     """
#     Real Stripe adapter implementing the complete PaymentPort interface.
#     """
    
#     def __init__(self):
#         stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
#         if not stripe.api_key:
#             raise ValueError("STRIPE_SECRET_KEY environment variable is required")

#     def create_hold(
#         self,
#         *,
#         amount: Decimal,
#         currency: str,
#         reference: str,
#     ) -> str:
#         """Create authorization hold - uses create_payment_intent internally"""
#         intent_data = self.create_payment_intent(
#             amount=amount,
#             currency=currency,
#             reference=reference,
#             capture_method="manual"
#         )
#         return intent_data["payment_intent_id"]

#     def create_payment_intent(
#         self,
#         *,
#         amount: Decimal,
#         currency: str,
#         reference: str,
#         capture_method: str = "manual",
#     ) -> dict:
#         """Create PaymentIntent for frontend Stripe Elements"""
#         try:
#             intent = stripe.PaymentIntent.create(
#                 amount=int(amount * 100),
#                 currency=currency.lower(),
#                 capture_method=capture_method,
#                 metadata={"booking_id": reference},
#                 payment_method_types=["card"],
#             )
#             return {
#                 "payment_intent_id": intent.id,
#                 "client_secret": intent.client_secret,
#                 "status": intent.status,
#                 "amount": amount,
#                 "currency": currency
#             }
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe error: {str(e)}")

#     def confirm_payment_intent(
#         self,
#         *,
#         payment_intent_id: str,
#     ) -> dict:
#         """Confirm PaymentIntent after frontend collection"""
#         try:
#             intent = stripe.PaymentIntent.retrieve(payment_intent_id)
#             #If you need to confirm server-side
#             #intent = stripe.PaymentIntent.confirm(payment_intent_id)
#             return {
#                 "status": intent.status,
#                 "payment_intent_id": intent.id
#             }
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe confirmation error: {str(e)}")

#     def get_payment_intent(
#         self,
#         *,
#         payment_intent_id: str,
#     ) -> Optional[dict]:
#         """Retrieve PaymentIntent status"""
#         try:
#             intent = stripe.PaymentIntent.retrieve(payment_intent_id)
#             return {
#                 "id": intent.id,
#                 "status": intent.status,
#                 "amount": Decimal(intent.amount) / 100,
#                 "currency": intent.currency,
#                 "client_secret": intent.client_secret,
#                 "capture_method": intent.capture_method
#             }
#         except stripe.error.StripeError:
#             return None

#     def capture(
#         self,
#         *,
#         processor_ref: str,
#     ) -> None:
#         """Capture authorized payment"""
#         try:
#             stripe.PaymentIntent.capture(processor_ref)
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe capture error: {str(e)}")

#     def cancel_payment_intent(
#         self,
#         *,
#         processor_ref: str,
#     ) -> None:
#         """Cancel a payment intent (for uncaptured payments)"""
#         try:
#             stripe.PaymentIntent.cancel(processor_ref)
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe cancel error: {str(e)}")

#     def refund(
#         self,
#         *,
#         processor_ref: str,
#         amount: Decimal,
#     ) -> None:
#         """Refund payment (for captured payments)"""
#         try:
#             stripe.Refund.create(
#                 payment_intent=processor_ref,
#                 amount=int(amount * 100),
#             )
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe refund error: {str(e)}")

#     #update tests
#     def create_checkout_session(
#         self,
#         *,
#         booking_id: str,
#         amount: Decimal,
#         currency: str,
#         success_url: str,
#         cancel_url: str,
#         customer_email: str = None,
#     ) -> Dict[str, Any]:
#         """Create Stripe Checkout Session for hosted payment page"""
#         try:
#             session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=[{
#                     'price_data': {
#                         'currency': currency.lower(),
#                         'product_data': {
#                             'name': f'Server Booking #{booking_id}',
#                             'description': 'Remote server rental booking',
#                         },
#                         'unit_amount': int(amount * 100),  #cents
#                     },
#                     'quantity': 1,
#                 }],
#                 mode='payment',
#                 success_url=success_url,
#                 cancel_url=cancel_url,
#                 client_reference_id=booking_id,
#                 customer_email=customer_email,
#                 metadata={
#                     'booking_id': booking_id,
#                 }
#             )
#             return {
#                 'session_id': session.id,
#                 'url': session.url,
#                 'payment_intent_id': session.payment_intent,
#             }
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe Checkout error: {str(e)}")

#     def retrieve_checkout_session(
#         self,
#         *,
#         session_id: str,
#     ) -> Dict[str, Any]:
#         """Retrieve Checkout Session details"""
#         try:
#             session = stripe.checkout.Session.retrieve(session_id)
#             return {
#                 'id': session.id,
#                 'payment_status': session.payment_status,
#                 'payment_intent': session.payment_intent,
#                 'customer_email': session.customer_email,
#                 'amount_total': Decimal(session.amount_total) / 100 if session.amount_total else None,
#                 'currency': session.currency,
#                 'metadata': session.metadata,
#             }
#         except stripe.error.StripeError as e:
#             raise ValueError(f"Stripe retrieval error: {str(e)}")
#     #update tests


# class MockStripeAdapter(PaymentPort):
#     """
#     Mock adapter implementing the complete PaymentPort interface.
#     """
#     def create_hold(self, *, amount, currency, reference) -> str:
#         return f"pi_mock_{uuid.uuid4().hex}"

#     def create_payment_intent(self, *, amount, currency, reference, capture_method="manual") -> dict:
#         payment_intent_id = f"pi_mock_{uuid.uuid4().hex}"
#         return {
#             "payment_intent_id": payment_intent_id,
#             "client_secret": f"cs_mock_{uuid.uuid4().hex}",
#             "status": "requires_payment_method",
#             "amount": amount,
#             "currency": currency
#         }

#     def confirm_payment_intent(self, *, payment_intent_id) -> dict:
#         return {"status": "succeeded", "payment_intent_id": payment_intent_id}

#     def get_payment_intent(self, *, payment_intent_id) -> Optional[dict]:
#         return {
#             "id": payment_intent_id,
#             "status": "succeeded",
#             "amount": Decimal("100.00"),
#             "currency": "usd",
#             "client_secret": f"cs_mock_{uuid.uuid4().hex}",
#             "capture_method": "manual"
#         }

#     def capture(self, *, processor_ref) -> None:
#         return None

#     def refund(self, *, processor_ref, amount) -> None:
#         return None
    
#     def cancel_payment_intent(self, *, processor_ref) -> None:
#         return None

#     #update tests
#     def create_checkout_session(
#         self,
#         *,
#         booking_id: str,
#         amount: Decimal,
#         currency: str,
#         success_url: str,
#         cancel_url: str,
#         customer_email: str = None,
#     ) -> Dict[str, Any]:
#         """Mock Checkout Session creation"""
#         mock_session_id = f"cs_mock_{uuid.uuid4().hex}"
#         mock_url = f"https://checkout.stripe.com/pay/{mock_session_id}"
        
#         return {
#             'session_id': mock_session_id,
#             'url': mock_url,
#             'payment_intent_id': f"pi_mock_{uuid.uuid4().hex}",
#         }

#     def retrieve_checkout_session(
#         self,
#         *,
#         session_id: str,
#     ) -> Dict[str, Any]:
#         """Mock Checkout Session retrieval"""
#         return {
#             'id': session_id,
#             'payment_status': 'paid',
#             'payment_intent': f"pi_mock_{uuid.uuid4().hex}",
#             'customer_email': 'test@example.com',
#             'amount_total': Decimal("100.00"),
#             'currency': 'usd',
#             'metadata': {'booking_id': 'mock_booking_id'},
#         }
#     #update tests

# def get_payment_adapter() -> PaymentPort:
#     """Factory function returning PaymentPort interface"""
#     if os.getenv("USE_REAL_STRIPE", "false").lower() == "true":
#         return RealStripeAdapter()
#     else:
#         return MockStripeAdapter()