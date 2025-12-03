import pytest
from unittest.mock import Mock, MagicMock 
from uuid import uuid4
from decimal import Decimal

from app.payments.service import PaymentsService
from app.payments.repository import PaymentsRepository
from app.payments.ports.payment_port import PaymentPort
from app.payments.models import Payment, PaymentType, PaymentStatus
from app.providers.public import ProvidersPublic
from app.notifications.public import NotificationsPublic

import stripe

@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()


@pytest.fixture
def mock_repository():
    """Mock PaymentsRepository fixture"""
    return Mock(spec=PaymentsRepository)


@pytest.fixture
def mock_port():
    """Mock PaymentPort fixture"""
    return Mock(spec=PaymentPort)


@pytest.fixture
def mock_providers_public():
    """Mock ProvidersPublic fixture"""
    return Mock(spec=ProvidersPublic)


@pytest.fixture
def mock_notifications_public():
    """Mock NotificationsPublic fixture"""
    return Mock(spec=NotificationsPublic)


@pytest.fixture
def payments_service(mock_db, mock_repository, mock_port, mock_providers_public, mock_notifications_public):
    """PaymentsService fixture with all dependencies"""
    return PaymentsService(
        db=mock_db,
        repo=mock_repository,
        port=mock_port,
        providers_public=mock_providers_public,
        notifications_public=mock_notifications_public
    )


@pytest.fixture
def sample_booking():
    """Fixture for a mock booking object"""
    booking = Mock()
    booking.id = uuid4()
    booking.buyer = Mock()
    return booking


@pytest.fixture
def sample_escrow_payment():
    """Fixture for a mock escrow payment object"""
    payment = Mock(spec=Payment)
    payment.id = uuid4()
    payment.booking_id = uuid4()
    payment.type = PaymentType.ESCROW
    payment.processor_ref = "pi_123456789"
    payment.amount = Decimal("100.00")
    payment.currency = "USD"
    payment.status = PaymentStatus.AUTHORIZED
    return payment


@pytest.fixture
def sample_refund_payment():
    """Fixture for a mock refund payment object"""
    payment = Mock(spec=Payment)
    payment.id = uuid4()
    payment.booking_id = uuid4()
    payment.type = PaymentType.REFUND
    payment.processor_ref = "re_123456789"
    payment.amount = Decimal("100.00")
    payment.currency = "USD"
    payment.status = PaymentStatus.REFUNDED
    return payment


@pytest.fixture
def sample_payment_intent_response():
    """Fixture for Stripe PaymentIntent response"""
    return {
        "client_secret": "pi_123_secret_abc",
        "payment_intent_id": "pi_123456789",
        "amount": Decimal("100.00"),
        "currency": "USD"
    }


class TestPaymentsService:
    
    #def create_escrow(self, db: Session, *, booking, amount: Decimal, currency: str) -> Payment:
    def test_create_escrow_successfully_creates_authorization_hold(
        self, payments_service, mock_db, mock_port, mock_repository, sample_booking, sample_escrow_payment
    ):
        """Test successful escrow creation with external payment processor"""
        #Mock port.create_hold to return processor reference
        #Mock repository.create_payment to return created payment
        #Call service.create_escrow with booking, amount, and currency
        #Verify port.create_hold was called with correct parameters
        #Verify payment was created with correct fields (type=ESCROW, status=AUTHORIZED)
        #Verify repository.create_payment was called with the payment
        #Verify the created payment is returned
        processor_ref = "re_123456789"
        mock_payment = sample_escrow_payment
        amount = Decimal("100.00")
        currency = "USD"

        mock_port.create_hold.return_value = processor_ref
        mock_repository.create_payment.return_value = mock_payment

        result = payments_service.create_escrow(sample_booking, amount, currency)

        mock_port.create_hold.assert_called_once_with(amount=amount, currency=currency, reference=str(sample_booking.id))
        assert result.type == PaymentType.ESCROW
        assert result.status == PaymentStatus.AUTHORIZED
        mock_repository.create_payment.assert_called_once()
        assert result == mock_payment

    def test_create_escrow_handles_external_api_failure_gracefully(
        self, payments_service, mock_repository, mock_port, sample_booking
    ):
        """Test escrow creation fails when payment processor API fails"""
        #Mock port.create_hold to raise an exception
        #Call service.create_escrow with booking, amount, and currency
        #Verify the exception is propagated
        #Verify repository.create_payment is NOT called
        amount = Decimal("100.00")
        currency = "USD"

        mock_port.create_hold.side_effect = ValueError("Could not create a payment hold.")

        with pytest.raises(ValueError, match="Could not create a payment hold."):
            payments_service.create_escrow(sample_booking, amount, currency)

        mock_repository.create_payment.assert_not_called()

    #def capture(self, db: Session, *, booking) -> Payment:
    def test_capture_successfully_captures_authorized_escrow(
        self, payments_service, mock_db, mock_repository, mock_port, mock_notifications_public, sample_booking, sample_escrow_payment
    ):
        """Test successful capture of authorized escrow payment"""
        #Mock repository.get_latest_escrow to return authorized escrow payment
        #Mock port.capture to succeed
        #Mock repository.update_payment to return updated payment
        #Call service.capture with booking
        #Verify repository.get_latest_escrow was called with booking ID
        #Verify port.capture was called with processor_ref
        #Verify payment status updated to CAPTURED
        #Verify repository.update_payment was called
        #Verify notifications.payment_captured was called with buyer and payment
        #Verify updated payment is returned
        mock_escrow = sample_escrow_payment
        mock_escrow.status = PaymentStatus.AUTHORIZED
        mock_updated_payment = Mock(spec=Payment)
        mock_updated_payment.status = PaymentStatus.CAPTURED
        
        mock_repository.get_latest_escrow.return_value = mock_escrow
        mock_repository.update_payment.return_value = mock_updated_payment
        
        result = payments_service.capture(sample_booking)
        
        mock_repository.get_latest_escrow.assert_called_once_with(mock_db, sample_booking.id)
        mock_port.capture.assert_called_once_with(processor_ref=mock_escrow.processor_ref)
        mock_repository.update_payment.assert_called_once_with(mock_db, mock_escrow)
        mock_notifications_public.payment_captured.assert_called_once_with(sample_booking.buyer, mock_updated_payment)
        assert result == mock_updated_payment

    def test_capture_raises_error_when_no_escrow_found(
        self, payments_service, mock_port, mock_repository, sample_booking
    ):
        """Test capture fails when no escrow exists for booking"""
        #Mock repository.get_latest_escrow to return None
        #Call service.capture with booking
        #Verify ValueError is raised with correct message
        #Verify port.capture is NOT called
        mock_repository.get_latest_escrow.return_value = None

        with pytest.raises(ValueError, match="No escrow found to capture."):
            payments_service.capture(sample_booking)

        mock_port.capture.assert_not_called()

    def test_capture_raises_error_when_escrow_not_authorized(
        self, payments_service, mock_port, mock_repository, sample_booking, sample_escrow_payment
    ):
        """Test capture fails when escrow is not in AUTHORIZED state"""
        #Mock repository.get_latest_escrow to return escrow with non-AUTHORIZED status
        #Call service.capture with booking
        #Verify ValueError is raised with correct message
        #Verify port.capture is NOT called
        mock_escrow = sample_escrow_payment
        mock_escrow.status = PaymentStatus.REFUNDED

        mock_repository.get_latest_escrow.return_value = mock_escrow

        with pytest.raises(ValueError, match="Escrow already captured or refunded."):
            payments_service.capture(sample_booking)

        mock_port.capture.assert_not_called()

    def test_capture_handles_external_capture_failure(
        self, payments_service, mock_db, mock_repository, mock_port, sample_booking, sample_escrow_payment
    ):
        """Test capture fails when payment processor capture fails"""
        #Mock repository.get_latest_escrow to return authorized escrow
        #Mock port.capture to raise exception
        #Call service.capture with booking
        #Verify exception is propagated
        #Verify repository.update_payment is NOT called
        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.capture.side_effect = ValueError("Could not capture payment.")

        with pytest.raises(ValueError, match="Could not capture payment."):
            payments_service.capture(sample_booking)

        mock_repository.update_payment.assert_not_called()

    #def void_escrow(self, db: Session, *, booking) -> Payment:
    def test_void_escrow_successfully_cancels_authorized_payment(
        self, payments_service, mock_db, mock_repository, mock_port, sample_booking, sample_escrow_payment
    ):
        """Test successful void of authorized escrow payment"""
        #Mock repository.get_latest_escrow to return authorized escrow
        #Mock port.cancel_payment_intent to succeed
        #Mock repository.update_payment to return updated payment
        #Call service.void_escrow with booking
        #Verify repository.get_latest_escrow was called
        #Verify port.cancel_payment_intent was called with processor_ref
        #Verify payment status updated to CANCELLED
        #Verify repository.update_payment was called
        #Verify updated payment is returned
        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.cancel_payment_intent.return_value = None

        mock_repository.update_payment.return_value = sample_escrow_payment
        result = payments_service.void_escrow(sample_booking)

        mock_repository.get_latest_escrow.assert_called_once_with(mock_db, sample_booking.id)
        mock_port.cancel_payment_intent.assert_called_once_with(processor_ref=sample_escrow_payment.processor_ref)
        assert result.status == PaymentStatus.CANCELLED
        mock_repository.update_payment.assert_called_once_with(mock_db, sample_escrow_payment)
        assert result == sample_escrow_payment

    def test_void_escrow_raises_error_when_no_escrow_found(
        self, payments_service, mock_port, mock_repository, sample_booking
    ):
        """Test void fails when no escrow exists for booking"""
        #Mock repository.get_latest_escrow to return None
        #Call service.void_escrow with booking
        #Verify ValueError is raised with correct message
        #Verify port.cancel_payment_intent is NOT called
        mock_repository.get_latest_escrow.return_value = None

        with pytest.raises(ValueError, match="No escrow found to void."):
            payments_service.void_escrow(sample_booking)  

        mock_port.cancel_payment_intent.assert_not_called()      

    def test_void_escrow_raises_error_when_escrow_not_authorized(
        self, payments_service, mock_repository, sample_booking, sample_escrow_payment, mock_port
    ):
        """Test void fails when escrow is not in AUTHORIZED state"""
        #Mock repository.get_latest_escrow to return escrow with non-AUTHORIZED status
        #Call service.void_escrow with booking
        #Verify ValueError is raised with correct message
        #Verify port.cancel_payment_intent is NOT called
        sample_escrow_payment.status = PaymentStatus.CAPTURED

        mock_repository.get_latest_escrow.return_value = sample_escrow_payment

        with pytest.raises(ValueError, match=f"Cannot void escrow in status: {sample_escrow_payment.status}. Only AUTHORIZED payments can be voided."):
            payments_service.void_escrow(sample_booking)  

        mock_port.cancel_payment_intent.assert_not_called()    

    #def refund(self, db: Session, *, booking, reason: str | None = None) -> Payment:
    def test_refund_successfully_refunds_authorized_escrow(
        self, payments_service, mock_db, mock_repository, mock_port, sample_booking, sample_escrow_payment, sample_refund_payment
    ):
        """Test successful refund of authorized escrow payment"""
        #Mock repository.get_latest_escrow to return authorized escrow
        #Mock port.refund to succeed
        #Mock repository.create_payment to return refund payment
        #Call service.refund with booking
        #Verify repository.get_latest_escrow was called
        #Verify port.refund was called with processor_ref and amount
        #Verify refund payment created with type=REFUND, status=REFUNDED
        #Verify repository.create_payment was called with refund payment
        #Verify refund payment is returned
        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.refund.return_value = None
        mock_repository.create_payment.return_value = sample_refund_payment
        
        result = payments_service.refund(sample_booking)

        mock_repository.get_latest_escrow.assert_called_once_with(mock_db, sample_booking.id)
        mock_port.refund.assert_called_once_with(processor_ref=sample_escrow_payment.processor_ref, amount=sample_escrow_payment.amount)
        assert result.type == PaymentType.REFUND
        assert result.status == PaymentStatus.REFUNDED
        mock_repository.create_payment.assert_called_once()
        assert result == sample_refund_payment

    def test_refund_successfully_refunds_captured_payment(
        self, payments_service, mock_repository, mock_port, sample_booking, sample_escrow_payment, sample_refund_payment
    ):
        """Test successful refund of captured payment (different scenario)"""
        #Set escrow status to CAPTURED instead of AUTHORIZED
        #Mock repository.get_latest_escrow to return captured escrow
        #Mock port.refund to succeed
        #Mock repository.create_payment to return refund payment
        #Call service.refund with booking
        #Verify port.refund still called (should work for captured payments)
        #Verify refund payment created with correct fields
        sample_escrow_payment.status = PaymentStatus.CAPTURED

        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.refund.return_value = None
        mock_repository.create_payment.return_value = sample_refund_payment
        
        result = payments_service.refund(sample_booking)
        mock_port.refund.assert_called_once_with(processor_ref=sample_escrow_payment.processor_ref, amount=sample_escrow_payment.amount)
        assert result == sample_refund_payment

    def test_refund_raises_error_when_no_escrow_found(
        self, payments_service, mock_port, mock_repository, sample_booking
    ):
        """Test refund fails when no escrow exists for booking"""
        #Mock repository.get_latest_escrow to return None
        #Call service.refund with booking
        #Verify ValueError is raised with correct message
        #Verify port.refund is NOT called
        mock_repository.get_latest_escrow.return_value = None

        with pytest.raises(ValueError, match="No escrow found to refund."):
            payments_service.refund(sample_booking)

        mock_port.refund.assert_not_called()

    def test_refund_handles_external_refund_failure(
        self, payments_service, mock_repository, mock_port, sample_booking, sample_escrow_payment
    ):
        """Test refund fails when payment processor refund fails"""
        #Mock repository.get_latest_escrow to return escrow
        #Mock port.refund to raise exception
        #Call service.refund with booking
        #Verify exception is propagated
        #Verify repository.create_payment is NOT called
        mock_repository.get_latest_escrow.return_value = sample_escrow_payment
        mock_port.refund.side_effect = ValueError("Unable to process refund with Stripe.")

        with pytest.raises(ValueError, match="Unable to process refund with Stripe."):
            payments_service.refund(sample_booking)
        
        mock_repository.create_payment.assert_not_called()

    #def list_for_booking(self, db: Session, booking_id):
    def test_list_for_booking_delegates_to_repository(
        self, payments_service, mock_db, mock_repository, sample_booking
    ):
        """Test payment listing for booking delegates to repository"""
        #Create booking_id
        #Mock repository.list_payments_for_booking to return list of payments
        #Call service.list_for_booking with booking_id
        #Verify repository.list_payments_for_booking was called with correct parameters
        #Verify list of payments is returned
        booking_id = sample_booking.id
        mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]

        mock_repository.list_payments_for_booking.return_value = mock_payments

        result = payments_service.list_for_booking(booking_id)
        mock_repository.list_payments_for_booking.assert_called_once_with(mock_db, booking_id)
        assert result == mock_payments

    def test_list_for_booking_returns_empty_list_when_no_payments(
        self, payments_service, mock_repository, sample_booking
    ):
        """Test payment listing returns empty list when no payments exist"""
        #Mock repository.list_payments_for_booking to return empty list
        #Call service.list_for_booking with booking_id
        #Verify empty list is returned
        mock_repository.list_payments_for_booking.return_value = []
        result = payments_service.list_for_booking(sample_booking.id)

        assert result == []

    #def get_payments_for_bookings(self, db: Session, booking_ids: list[UUID]):
    def test_get_payments_for_bookings_delegates_to_repository(
        self, payments_service, mock_db, mock_repository
    ):
        """Test getting payments for multiple bookings delegates to repository"""
        #Create list of booking_ids
        #Mock repository.list_payments_for_bookings to return list of payments
        #Call service.get_payments_for_bookings with booking_ids
        #Verify repository.list_payments_for_bookings was called with correct parameters
        #Verify list of payments is returned
        booking_ids = [uuid4(), uuid4()]
        mock_payments = [Mock(spec=Payment), Mock(spec=Payment)]

        mock_repository.list_payments_for_bookings.return_value = mock_payments
        result = payments_service.get_payments_for_bookings(booking_ids)    
        mock_repository.list_payments_for_bookings.assert_called_once_with(mock_db, booking_ids)
        assert result == mock_payments

    def test_get_payments_for_bookings_handles_empty_booking_ids(
        self, payments_service, mock_db, mock_repository
    ):
        """Test getting payments for empty booking_ids list"""
        #Call service.get_payments_for_bookings with empty list
        #Verify repository.list_payments_for_bookings was called with empty list
        #Verify empty list is returned
        empty_list = []
        mock_repository.list_payments_for_bookings.return_value = []
        result = payments_service.get_payments_for_bookings(empty_list)

        mock_repository.list_payments_for_bookings.assert_called_once_with(mock_db, empty_list)
        assert result == []

    #def create_payment_intent(self, db: Session, *, booking_id: UUID, amount: Decimal, currency: str = "USD") -> dict:
    def test_create_payment_intent_successfully_creates_stripe_intent(
        self, payments_service, mock_repository, monkeypatch
    ):
        """Test successful Stripe PaymentIntent creation for frontend"""
        #Mock stripe.PaymentIntent.create to return intent with client_secret
        #Mock repository.create_payment to return payment
        #Call service.create_payment_intent with booking_id, amount, currency
        #Verify stripe.PaymentIntent.create called with correct parameters
        #Verify payment created with type=ESCROW, status=AUTHORIZED
        #Verify repository.create_payment called with payment
        #Verify response dict contains client_secret and payment details
        booking_id = uuid4()
        amount = Decimal("100.00")
        currency = "USD"
        
        mock_intent = Mock()
        mock_intent.id = "pi_123456789"
        mock_intent.client_secret = "pi_123_secret_abc"
        
        mock_payment = Mock(spec=Payment)
        mock_payment.type = PaymentType.ESCROW
        mock_payment.status = PaymentStatus.AUTHORIZED
        
        mock_stripe_create = Mock(return_value=mock_intent)
        monkeypatch.setattr(stripe.PaymentIntent, "create", mock_stripe_create)
        
        mock_repository.create_payment.return_value = mock_payment
        
        result = payments_service.create_payment_intent(booking_id, amount, currency)
        
        mock_stripe_create.assert_called_once_with(
            amount=int(amount * 100),
            currency=currency.lower(),
            capture_method="manual",
            metadata={"booking_id": str(booking_id)},
            payment_method_types=["card"]
        )
        
        mock_repository.create_payment.assert_called_once()
        call_args = mock_repository.create_payment.call_args
        created_payment = call_args[0][1]
        assert created_payment.type == PaymentType.ESCROW
        assert created_payment.status == PaymentStatus.AUTHORIZED
        
        assert result["client_secret"] == mock_intent.client_secret
        assert result["payment_intent_id"] == mock_intent.id
        assert result["amount"] == amount
        assert result["currency"] == currency

    def test_create_payment_intent_handles_stripe_api_failure(
        self, payments_service, sample_booking, monkeypatch, mock_repository
    ):
        """Test PaymentIntent creation fails when Stripe API fails"""
        #Mock stripe.PaymentIntent.create to raise exception
        #Call service.create_payment_intent with booking_id, amount, currency
        #Verify exception is propagated
        #Verify repository.create_payment is NOT called
        amount = Decimal("100.00")
        currency = "USD"
        mock_intent = Mock()
        mock_stripe_create = Mock(side_effect=ValueError("Stripe error: couldn't create payment intent"))

        monkeypatch.setattr(stripe.PaymentIntent, "create", mock_stripe_create)

        with pytest.raises(ValueError, match="Stripe error: couldn't create payment intent"):
            payments_service.create_payment_intent(sample_booking.id, amount, currency)
        
        mock_repository.create_payment.assert_not_called()

    def test_create_payment_intent_uses_correct_amount_conversion(
        self, payments_service, mock_repository, monkeypatch
    ):
        """Test PaymentIntent amount is correctly converted to cents"""
        #Mock stripe.PaymentIntent.create to capture its arguments
        #Call service.create_payment_intent with amount in dollars
        #Verify amount multiplied by 100 (converted to cents)
        #Verify payment created with original amount (not cents)
        booking_id = uuid4()
        amount = Decimal("150.75")
        currency = "USD"
        
        captured_args = {}
        def mock_stripe_create(**kwargs):
            captured_args.update(kwargs)
            mock_intent = Mock()
            mock_intent.id = "pi_123"
            mock_intent.client_secret = "secret"
            return mock_intent
        
        monkeypatch.setattr(stripe.PaymentIntent, "create", mock_stripe_create)
        
        mock_payment = Mock(spec=Payment)
        mock_repository.create_payment.return_value = mock_payment
        
        result = payments_service.create_payment_intent(booking_id, amount, currency)
        
        assert captured_args["amount"] == int(amount * 100)
        
        call_args = mock_repository.create_payment.call_args
        created_payment = call_args[0][1]
        assert created_payment.amount == amount