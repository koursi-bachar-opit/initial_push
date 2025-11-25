import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.bookings.public import BookingsPublicImpl, get_bookings_public
from app.bookings.models import Booking, BookingStatus


class TestBookingsPublicImpl:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_service = Mock()
        #Set up the BookingStatus enum on the mock service
        self.mock_service.BookingStatus = BookingStatus
        self.public_impl = BookingsPublicImpl(self.mock_service)
    
    def test_get_booking_calls_service(self):
        """Test that get_booking delegates to service layer."""
        
        booking_id = uuid4()
        expected_booking = Mock(spec=Booking)
        self.mock_service.get_booking_readonly.return_value = expected_booking
        
        
        result = self.public_impl.get_booking(booking_id)

        self.mock_service.get_booking_readonly.assert_called_once_with(booking_id)
        assert result == expected_booking

    @pytest.mark.parametrize("status,expected", [
        (BookingStatus.ACTIVE, True),
        (BookingStatus.REQUESTED, False),
        (BookingStatus.CONFIRMED, False),
        (BookingStatus.COMPLETED, False),
        (BookingStatus.CANCELLED, False),
    ])
    def test_is_active_checks_status(self, status, expected):
        """Test is_active returns True only for ACTIVE status."""
        
        booking = Mock(spec=Booking, status=status)
        
        result = self.public_impl.is_active(booking)

        assert result == expected

    @pytest.mark.parametrize("status,expected", [
        (BookingStatus.CONFIRMED, True),
        (BookingStatus.REQUESTED, False),
        (BookingStatus.ACTIVE, False),
        (BookingStatus.COMPLETED, False),
        (BookingStatus.CANCELLED, False),
    ])
    def test_is_confirmed_checks_status(self, status, expected):
        """Test is_confirmed returns True only for CONFIRMED status."""
        
        booking = Mock(spec=Booking, status=status)

        result = self.public_impl.is_confirmed(booking)

        assert result == expected

    @pytest.mark.parametrize("status,expected", [
        (BookingStatus.REQUESTED, True),
        (BookingStatus.CONFIRMED, False),
        (BookingStatus.ACTIVE, False),
        (BookingStatus.COMPLETED, False),
        (BookingStatus.CANCELLED, False),
    ])
    def test_is_requested_checks_status(self, status, expected):
        """Test is_requested returns True only for REQUESTED status."""
        
        booking = Mock(spec=Booking, status=status)
        
        result = self.public_impl.is_requested(booking)

        assert result == expected

    @pytest.mark.parametrize("status,expected", [
        (BookingStatus.CANCELLED, True),
        (BookingStatus.REQUESTED, False),
        (BookingStatus.CONFIRMED, False),
        (BookingStatus.ACTIVE, False),
        (BookingStatus.COMPLETED, False),
    ])
    def test_is_cancelled_checks_status(self, status, expected):
        """Test is_cancelled returns True only for CANCELLED status."""
        
        booking = Mock(spec=Booking, status=status)
        
        result = self.public_impl.is_cancelled(booking)

        assert result == expected

    @pytest.mark.parametrize("status,expected", [
        (BookingStatus.COMPLETED, True),
        (BookingStatus.REQUESTED, False),
        (BookingStatus.CONFIRMED, False),
        (BookingStatus.ACTIVE, False),
        (BookingStatus.CANCELLED, False),
    ])
    def test_is_completed_checks_status(self, status, expected):
        """Test is_completed returns True only for COMPLETED status."""
        
        booking = Mock(spec=Booking, status=status)
        
        result = self.public_impl.is_completed(booking)

        assert result == expected

    @pytest.mark.parametrize("status,expected", [
        (BookingStatus.REQUESTED, True),
        (BookingStatus.CONFIRMED, True),
        (BookingStatus.ACTIVE, False),
        (BookingStatus.COMPLETED, False),
        (BookingStatus.CANCELLED, False),
    ])
    def test_is_cancellable_checks_cancellable_statuses(self, status, expected):
        """Test is_cancellable returns True for REQUESTED and CONFIRMED statuses."""
        
        booking = Mock(spec=Booking, status=status)
        
        result = self.public_impl.is_cancellable(booking)

        assert result == expected


class TestBookingsPublicDependency:
    def test_get_bookings_public_returns_impl(self):
        """Test that get_bookings_public returns BookingsPublicImpl instance."""
        
        mock_service = Mock()
        mock_service.BookingStatus = BookingStatus  
        
        result = get_bookings_public(service=mock_service)

        assert isinstance(result, BookingsPublicImpl)
        assert result.service == mock_service

    def test_get_bookings_public_implements_protocol(self):
        """Test that returned instance implements the BookingsPublic protocol."""
        
        mock_service = Mock()
        mock_service.BookingStatus = BookingStatus  
        
        result = get_bookings_public(service=mock_service)
        
        #Check that all protocol methods exist and are callable
        assert hasattr(result, 'get_booking')
        assert hasattr(result, 'is_active')
        assert hasattr(result, 'is_confirmed')
        assert hasattr(result, 'is_requested')
        assert hasattr(result, 'is_cancelled')
        assert hasattr(result, 'is_completed')
        assert hasattr(result, 'is_cancellable')
        
        #Verify they are callable methods
        assert callable(result.get_booking)
        assert callable(result.is_active)
        assert callable(result.is_confirmed)
        assert callable(result.is_requested)
        assert callable(result.is_cancelled)
        assert callable(result.is_completed)
        assert callable(result.is_cancellable)


#simple verification that the pattern works with proper mocking
def test_booking_status_from_service_pattern():
    """Verify that getting BookingStatus from service works with proper mocking."""
    mock_service = Mock()
    mock_service.BookingStatus = BookingStatus
    public_impl = BookingsPublicImpl(mock_service)
    
    booking = Mock(status=BookingStatus.ACTIVE)
    result = public_impl.is_active(booking)
    assert result == True