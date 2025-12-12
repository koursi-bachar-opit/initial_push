import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.bookings.service import BookingsService
from app.bookings.repository import BookingsRepository
from app.bookings.models import Booking
from app.bookings.schemas import BookingRequest, BookingAdminCreate
from app.listings.models import Listing


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()


@pytest.fixture
def mock_repository():
    """Mock BookingsRepository fixture"""
    return Mock(spec=BookingsRepository)


@pytest.fixture
def mock_listings_public():
    """Mock ListingsPublic fixture for listing validation"""
    return Mock()


@pytest.fixture
def mock_credentials_public():
    """Mock AccessCredentialsPublic fixture for credential management"""
    return Mock()


@pytest.fixture
def mock_payments_public():
    """Mock PaymentsPublic fixture for escrow and payment processing"""
    return Mock()


@pytest.fixture
def mock_organizations_public():
    """Mock OrganizationsPublic fixture for org admin checks"""
    return Mock()


@pytest.fixture
def mock_compliance_public():
    """Mock CompliancePublic fixture for wipe attestation"""
    return Mock()


@pytest.fixture
def mock_notifications_public():
    """Mock NotificationsPublic fixture for notification sending"""
    return Mock()


@pytest.fixture
def bookings_service(
    mock_db,
    mock_repository,
    mock_listings_public,
    mock_credentials_public,
    mock_payments_public,
    mock_organizations_public,
    mock_compliance_public,
    mock_notifications_public
):
    """Main service fixture that composes all dependencies"""
    return BookingsService(
        db=mock_db,
        booking_repo=mock_repository,
        listings_public=mock_listings_public,
        credentials_public=mock_credentials_public,
        payments_public=mock_payments_public,
        organizations_public=mock_organizations_public,
        compliance_public=mock_compliance_public,
        notifications_public=mock_notifications_public
    )


@pytest.fixture
def sample_booking():
    """Fixture for a mock booking object"""
    booking = Mock(spec=Booking)
    booking.id = uuid4()
    booking.buyer_user_id = uuid4()
    booking.listing_id = uuid4()
    booking.start_time = datetime.now(timezone.utc)
    booking.end_time = datetime.now(timezone.utc)
    booking.status = "requested"
    booking.total_price_estimate = 100.0
    booking.listing = Mock(spec=Listing)
    booking.listing.hourly_price = 50.0
    booking.buyer = Mock()
    return booking


@pytest.fixture
def sample_booking_request():
    """Fixture for sample booking request data"""
    return BookingRequest(
        listing_id=uuid4(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        organization_id=None
    )


@pytest.fixture
def sample_booking_admin_create():
    """Fixture for sample admin booking creation data"""
    return BookingAdminCreate(
        listing_id=uuid4(),
        buyer_user_id=uuid4(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        organization_id=None
    )


class TestBookingsService:
    #Helper method tests
    #def normalize_times(self, start_time, end_time):
    def test_normalize_times_converts_to_utc(self, bookings_service):
        """Test time normalization converts aware datetimes to UTC"""
        #Create timezone-aware datetime objects with different timezones
        #Call normalize_times with start and end times
        #Verify both times are converted to UTC timezone
        #Verify the original times are preserved as UTC equivalents
        est_offset = timezone(timedelta(hours=-5))
        start_time = datetime(2026, 1, 15, 10, 0, 0, tzinfo=est_offset)
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        end_time = datetime(2026, 1, 15, 22, 0, 0, tzinfo=ist_offset)
        
        start_utc, end_utc = bookings_service.normalize_times(start_time, end_time)
        
        assert start_utc.tzinfo == timezone.utc
        assert end_utc.tzinfo == timezone.utc
        
        assert start_utc == start_time.astimezone(timezone.utc)
        assert end_utc == end_time.astimezone(timezone.utc)
        
        assert start_utc.hour == 15
        assert end_utc.hour == 16
        assert end_utc.minute == 30

    def test_normalize_times_raises_error_for_naive_datetimes(self, bookings_service):
        """Test time normalization raises error for naive datetimes"""
        #Create naive datetime objects (no timezone)
        #Call normalize_times with naive datetimes
        #Verify ValueError is raised
        start_time = datetime(2026, 1, 14, 22, 0, 0)
        end_time = datetime(2026, 1, 15, 22, 0, 0)

        with pytest.raises(ValueError, match="start_time and end_time must be timezone-aware"):
            bookings_service.normalize_times(start_time, end_time)

    #def validate_booking_window(self, start_utc, end_utc):
    def test_validate_booking_window_validates_start_before_end(self, bookings_service):
        """Test booking window validation with valid times"""
        #Create start_utc earlier than end_utc
        #Call validate_booking_window with valid times
        #Verify no exception is raised
        start_utc = datetime(2026, 1, 14, 22, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 22, 0, 0, tzinfo=timezone.utc)

        bookings_service.validate_booking_window(start_utc, end_utc)

    def test_validate_booking_window_raises_error_for_invalid_window(self, bookings_service):
        """Test validation raises error when end_utc <= start_utc"""
        #Create end_utc equal to start_utc
        #Call validate_booking_window
        #Verify ValueError is raised
        #Repeat with end_utc before start_utc
        start_utc = datetime(2026, 1, 15, 22, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 22, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="end_time must be after start_time"):
            bookings_service.validate_booking_window(start_utc, end_utc)

        start_utc = datetime(2026, 1, 15, 22, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 14, 22, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="end_time must be after start_time"):
            bookings_service.validate_booking_window(start_utc, end_utc)

    def test_validate_booking_window_raises_error_for_none_times(self, bookings_service):
        """Test validation raises error when times are None"""
        #Call validate_booking_window with start_utc=None
        #Verify ValueError is raised
        #Call validate_booking_window with end_utc=None
        #Verify ValueError is raised
        start_utc = None
        end_utc = datetime(2026, 1, 15, 22, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="start_time and end_time must be provided."):
            bookings_service.validate_booking_window(start_utc, end_utc)

        start_utc = datetime(2026, 1, 15, 22, 0, 0, tzinfo=timezone.utc)
        end_utc = None

        with pytest.raises(ValueError, match="start_time and end_time must be provided."):
            bookings_service.validate_booking_window(start_utc, end_utc)

    #def fetch_listing_or_raise(self, listing_id):
    def test_fetch_listing_or_raise_returns_listing_when_exists(self, bookings_service, mock_listings_public):
        """Test successful listing retrieval"""
        #Mock listings_public.get_listing_by_id to return a listing
        #Call fetch_listing_or_raise with listing ID
        #Verify correct listing is returned
        mock_listing = Mock(spec=Listing)
        listing_id = uuid4()

        mock_listings_public.get_listing_by_id.return_value = mock_listing
        result = bookings_service.fetch_listing_or_raise(listing_id)
        assert result == mock_listing

    def test_fetch_listing_or_raise_raises_error_when_listing_not_found(self, bookings_service, mock_listings_public):
        """Test error when listing doesn't exist"""
        #Mock listings_public.get_listing_by_id to return None
        #Call fetch_listing_or_raise with listing ID
        #Verify ValueError is raised
        listing_id = uuid4()

        mock_listings_public.get_listing_by_id.return_value = None
        with pytest.raises(ValueError, match="Listing not found"):
            bookings_service.fetch_listing_or_raise(listing_id)         

    #def calculate_price(self, start_time, end_time, hourly_price):
    def test_calculate_price_computes_correct_amount(self, bookings_service):
        """Test price calculation with valid inputs"""
        #Create start_time and end_time with specific duration
        #Set hourly_price to known value
        #Call calculate_price with these values
        #Verify calculated price matches expected formula: duration * (hourly_price / 3600)
        start_time = datetime(2026, 1, 15, 21, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2026, 1, 15, 23, 0, 0, tzinfo=timezone.utc)
        hourly_price = 35.0
        result = bookings_service.calculate_price(start_time, end_time, hourly_price)
        assert result == pytest.approx(70.0)

        start_time2 = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_time2 = datetime(2026, 1, 15, 11, 30, 0, tzinfo=timezone.utc)
        result2 = bookings_service.calculate_price(start_time2, end_time2, 40.0)
        assert result2 == pytest.approx(60.0)  # 1.5 × 40 = 60

    def test_calculate_price_raises_error_for_zero_or_negative_price(self, bookings_service):
        """Test error when hourly price is zero or negative"""
        #Call calculate_price with hourly_price = 0
        #Verify ValueError is raised
        #Call calculate_price with hourly_price = -10
        #Verify ValueError is raised
        start_time = Mock()
        end_time = Mock()

        hourly_price = 0
        with pytest.raises(ValueError, match="Hourly price must be greater than 0."):
            bookings_service.calculate_price(start_time, end_time, hourly_price)
        
        hourly_price = -10
        with pytest.raises(ValueError, match="Hourly price must be greater than 0."):
            bookings_service.calculate_price(start_time, end_time, hourly_price)
        
    #def build_booking_model(self, payload, buyer_user_id, start_utc, end_utc, total_price, organization_id=None):
    def test_build_booking_model_creates_booking_with_correct_fields(self, bookings_service, sample_booking_request):
        """Test booking model creation with all required fields"""
        #Create test data for buyer_user_id, times, price
        #Call build_booking_model with payload and test data
        #Verify returned Booking has correct listing_id, buyer_user_id, times
        #Verify status is set to REQUESTED
        #Verify total_price_estimate is set correctly
        payload = sample_booking_request
        buyer_user_id = uuid4()
        start_utc = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 20, 0, 0, tzinfo=timezone.utc)
        total_price = 25.0
        
        result = bookings_service.build_booking_model(payload, buyer_user_id, start_utc, end_utc, total_price)
        
        assert result.listing_id == payload.listing_id
        assert result.buyer_user_id == buyer_user_id
        assert result.start_time == start_utc
        assert result.end_time == end_utc
        assert result.status == bookings_service.BookingStatus.REQUESTED
        assert result.total_price_estimate == total_price
        assert result.organization_id is None

    def test_build_booking_model_includes_organization_id_when_provided(self, bookings_service, sample_booking_request):
        """Test booking model includes organization_id when specified"""
        #Create organization_id UUID
        #Call build_booking_model with organization_id parameter
        #Verify returned Booking has organization_id set
        payload = sample_booking_request
        buyer_user_id = uuid4()
        start_utc = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 20, 0, 0, tzinfo=timezone.utc)
        total_price = 25.0
        organization_id = uuid4()
        
        result = bookings_service.build_booking_model(payload, buyer_user_id, start_utc, end_utc, total_price, organization_id)

        assert result.organization_id == organization_id

    #Core service method tests
    def test_list_bookings_for_user_delegates_to_repository(self, bookings_service, mock_repository, mock_db):
        """Test user booking listing delegates to repository"""
        #Create user_id UUID
        #Mock repository.list_bookings_for_user to return list
        #Call service.list_bookings_for_user with user_id
        #Verify repository method called with correct parameters
        #Verify result matches repository return value
        user_id = uuid4()
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]

        mock_repository.list_bookings_for_user.return_value = mock_bookings

        result = bookings_service.list_bookings_for_user(user_id)

        assert result == mock_bookings
        mock_repository.list_bookings_for_user.assert_called_once_with(mock_db, user_id)

    def test_list_bookings_for_provider_delegates_to_repository(self, bookings_service, mock_repository, mock_db):
        """Test provider booking listing delegates to repository"""
        #Create provider_id UUID
        #Mock repository.list_bookings_for_provider to return list
        #Call service.list_bookings_for_provider with provider_id
        #Verify repository method called with correct parameters
        provider_id = uuid4()
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]

        mock_repository.list_bookings_for_provider.return_value = mock_bookings

        result = bookings_service.list_bookings_for_provider(provider_id)

        assert result == mock_bookings
        mock_repository.list_bookings_for_provider.assert_called_once_with(mock_db, provider_id)

    def test_list_all_bookings_delegates_to_repository(self, bookings_service, mock_repository, mock_db):
        """Test all bookings listing delegates to repository"""
        #Mock repository.list_bookings to return all bookings
        #Call service.list_all_bookings
        #Verify repository.list_bookings was called
        #Verify all bookings are returned
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]

        mock_repository.list_bookings.return_value = mock_bookings

        result = bookings_service.list_all_bookings()

        assert result == mock_bookings
        mock_repository.list_bookings.assert_called_once_with(mock_db)

    def test_get_booking_or_raise_returns_booking_when_exists(self, bookings_service, mock_repository, mock_db):
        """Test successful booking retrieval by ID"""
        #Create booking_id UUID
        #Mock repository.get_booking_by_id to return booking
        #Call _get_booking_or_raise with booking_id
        #Verify repository method was called with correct ID
        #Verify booking is returned
        booking_id = uuid4()
        mock_booking = Mock(spec=Booking)

        mock_repository.get_booking_by_id.return_value = mock_booking
        result = bookings_service._get_booking_or_raise(booking_id)

        assert result == mock_booking
        mock_repository.get_booking_by_id.assert_called_once_with(mock_db, booking_id)


    def test_get_booking_or_raise_raises_error_when_not_found(self, bookings_service, mock_repository, mock_db):
        """Test error when booking doesn't exist"""
        #Create booking_id UUID
        #Mock repository.get_booking_by_id to return None
        #Call _get_booking_or_raise with booking_id
        #Verify ValueError is raised
        booking_id = uuid4()

        mock_repository.get_booking_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Booking not found"):
            bookings_service._get_booking_or_raise(booking_id)

        mock_repository.get_booking_by_id.assert_called_once_with(mock_db, booking_id)

    def test_get_booking_readonly_calls_get_booking_or_raise(self, bookings_service):
        """Test readonly booking retrieval uses internal method"""
        #Patch _get_booking_or_raise to return booking
        #Call get_booking_readonly with booking_id
        #Verify _get_booking_or_raise was called
        #Verify booking is returned
        booking_id = uuid4()
        mock_booking = Mock(spec=Booking)

        with patch.object(bookings_service, '_get_booking_or_raise', return_value=mock_booking) as mock_get_booking:
            result = bookings_service.get_booking_readonly(booking_id)
        
        mock_get_booking.assert_called_once_with(booking_id)
        assert result == mock_booking

    #main business function calls
    #def admin_create_booking(self, payload: BookingAdminCreate):
    def test_admin_create_booking_creates_booking_successfully(self, bookings_service, sample_booking_admin_create, mock_repository, mock_db):
        """Test admin booking creation with valid data"""
        #Patch normalize_times to return times
        #Patch fetch_listing_or_raise to return listing
        #Patch calculate_price to return price
        #Patch build_booking_model to return booking
        #Mock repository.create_booking to return booking
        #Call admin_create_booking with payload
        #Verify all helper methods called in correct order
        #Verify booking is created and returned
        start_utc = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 15, 0, 0, tzinfo=timezone.utc)
        mock_listing = Mock(spec=Listing)
        mock_booking = Mock(spec=Booking)
        price = 150.0

        with patch.object(bookings_service, 'normalize_times', return_value=(start_utc, end_utc)) as mock_normalize, \
             patch.object(bookings_service, 'fetch_listing_or_raise', return_value=mock_listing) as mock_fetch, \
             patch.object(bookings_service, 'calculate_price', return_value=price) as mock_calc, \
             patch.object(bookings_service, 'build_booking_model', return_value=mock_booking) as mock_build:
            
            mock_repository.create_booking.return_value = mock_booking

            result = bookings_service.admin_create_booking(sample_booking_admin_create)
            
            assert result == mock_booking
            
            mock_normalize.assert_called_once_with(
                sample_booking_admin_create.start_time, 
                sample_booking_admin_create.end_time
            )
            mock_fetch.assert_called_once_with(sample_booking_admin_create.listing_id)
            mock_calc.assert_called_once_with(start_utc, end_utc, mock_listing.hourly_price)
            mock_build.assert_called_once_with(
                sample_booking_admin_create,
                sample_booking_admin_create.buyer_user_id,
                start_utc,
                end_utc,
                price,
                organization_id=sample_booking_admin_create.organization_id
            )
            mock_repository.create_booking.assert_called_once_with(
                mock_db, 
                mock_booking
            )

    #def request_booking(self, buyer_user_id, payload: BookingRequest):
    def test_request_booking_creates_booking_with_escrow(self, bookings_service, sample_booking_request, mock_repository, mock_payments_public, mock_db):
        """Test user booking request creates booking with escrow hold"""
        #Mock helper methods for time validation, listing fetch, price calc
        #Mock build_booking_model to return booking
        #Mock repository.create_booking to return created booking
        #Mock payments_public.escrow_for_booking
        #Call request_booking with buyer_id and payload
        #Verify booking created with REQUESTED status
        #Verify escrow_for_booking called with correct parameters
        #Verify created booking returned
        start_utc = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 15, 0, 0, tzinfo=timezone.utc)
        mock_listing = Mock(spec=Listing)
        mock_listing.hourly_price = 30.0
        mock_listing.currency = "USD"
        
        mock_booking = Mock(spec=Booking)
        mock_booking.status = bookings_service.BookingStatus.REQUESTED
        mock_booking.total_price_estimate = 150.0
        mock_booking.listing = mock_listing
        mock_booking.buyer = Mock()
        
        buyer_user_id = uuid4()
        
        bookings_service.normalize_times = Mock(return_value=(start_utc, end_utc))
        bookings_service.fetch_listing_or_raise = Mock(return_value=mock_listing)
        bookings_service.calculate_price = Mock(return_value=150.0)
        bookings_service.build_booking_model = Mock(return_value=mock_booking)
        
        mock_repository.create_booking.return_value = mock_booking
        
        result = bookings_service.request_booking(buyer_user_id, sample_booking_request)
        
        assert result == mock_booking
        mock_repository.create_booking.assert_called_once_with(mock_db, mock_booking)
        mock_payments_public.escrow_for_booking.assert_called_once_with(
            booking=mock_booking,
            amount=mock_booking.total_price_estimate,
            currency=mock_listing.currency
        )

    def test_request_booking_validates_organization_admin_when_org_specified(self, bookings_service, sample_booking_request, mock_organizations_public, mock_repository, mock_payments_public):
        """Test org admin validation when organization_id provided"""
        #Create payload with organization_id
        #Mock organizations_public.is_org_admin to return True
        #Mock other dependencies for successful booking
        #Call request_booking with buyer_id and org payload
        #Verify is_org_admin called with correct parameters
        #Verify booking creation proceeds
        start_utc = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 15, 0, 0, tzinfo=timezone.utc)
        
        buyer_user_id = uuid4()
        
        organization_id = uuid4()
        payload = sample_booking_request
        payload.organization_id = organization_id
        
        mock_listing = Mock(spec=Listing)
        mock_listing.hourly_price = 30.0
        mock_listing.currency = "USD"

        mock_booking = Mock(spec=Booking)
        mock_booking.status = bookings_service.BookingStatus.REQUESTED
        mock_booking.total_price_estimate = 150.0
        mock_booking.listing = mock_listing
        mock_booking.buyer = Mock()

        bookings_service.normalize_times = Mock(return_value=(start_utc, end_utc))
        bookings_service.fetch_listing_or_raise = Mock(return_value=mock_listing)
        bookings_service.calculate_price = Mock(return_value=150.0)
        bookings_service.build_booking_model = Mock(return_value=mock_booking)

        mock_organizations_public.is_org_admin.return_value = True
        
        mock_repository.create_booking.return_value = mock_booking
        
        result = bookings_service.request_booking(buyer_user_id, payload)

        mock_organizations_public.is_org_admin.assert_called_once_with(buyer_user_id, organization_id)

        assert result == mock_booking

        mock_repository.create_booking.assert_called_once()
        mock_payments_public.escrow_for_booking.assert_called_once()


    def test_request_booking_raises_error_when_not_org_admin(self, bookings_service, sample_booking_request, mock_organizations_public, mock_repository):
        """Test error when user is not org admin"""
        #Create payload with organization_id
        #Mock organizations_public.is_org_admin to return False
        #Call request_booking with buyer_id and org payload
        #Verify ValueError is raised
        #Verify no booking creation
        start_utc = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end_utc = datetime(2026, 1, 15, 15, 0, 0, tzinfo=timezone.utc)
        mock_listing = Mock(spec=Listing)
        
        buyer_user_id = uuid4()
        organization_id = uuid4()
        payload = sample_booking_request
        payload.organization_id = organization_id

        bookings_service.normalize_times = Mock(return_value=(start_utc, end_utc))
        bookings_service.fetch_listing_or_raise = Mock(return_value=mock_listing)
        bookings_service.calculate_price = Mock(return_value=150.0)

        mock_organizations_public.is_org_admin.return_value = False

        with pytest.raises(ValueError, match="User is not an admin of the specified organization"):
            bookings_service.request_booking(buyer_user_id, payload)
        
        mock_repository.create_booking.assert_not_called()


    def test_confirm_booking_transitions_from_requested_to_confirmed(self, bookings_service, sample_booking, mock_repository, mock_notifications_public, mock_db):
        """Test successful booking confirmation"""
        #Set booking status to REQUESTED
        #Set booking.end_time in future
        #Mock repository.update_booking to return booking
        #Mock notifications.booking_confirmed
        #Call confirm_booking with booking_id
        #Verify status changed to CONFIRMED
        #Verify repository.update_booking called
        #Verify booking_confirmed notification sent
        #Verify updated booking returned
        mock_booking = sample_booking
        mock_booking.end_time = datetime(2026, 1, 15, 20, 0, 0, tzinfo=timezone.utc)
        mock_booking.id = uuid4()

        mock_repository.update_booking.return_value = mock_booking

        result = bookings_service.confirm_booking(mock_booking.id, mock_booking)

        mock_notifications_public.booking_confirmed.assert_called_once_with(
            mock_booking.buyer, 
            mock_booking
        )
        assert result.status == bookings_service.BookingStatus.CONFIRMED
        mock_repository.update_booking.assert_called_once_with(mock_db, mock_booking)

    def test_confirm_booking_raises_error_when_listing_missing(self, bookings_service, sample_booking):
        """Test error when booking has no associated listing"""
        #Set booking.listing = None
        #Call confirm_booking with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.listing = None

        with pytest.raises(ValueError, match="Cannot confirm a booking without an associated listing"):
            bookings_service.confirm_booking(mock_booking.id, mock_booking)

    def test_confirm_booking_raises_error_after_end_time(self, bookings_service, sample_booking):
        """Test error when trying to confirm after booking end time"""
        #Set booking.end_time in the past
        #Call confirm_booking with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.end_time = datetime(2025, 1, 15, 20, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="Cannot confirm booking after booking end_time"):
            bookings_service.confirm_booking(mock_booking.id, mock_booking)

    def test_confirm_booking_raises_error_from_wrong_state(self, bookings_service, sample_booking):
        """Test error when confirming from non-requested state"""
        #Set booking.status to CONFIRMED
        #Call confirm_booking with booking
        #Verify ValueError is raised
        #Repeat for ACTIVE, COMPLETED, CANCELLED states
        mock_booking = sample_booking
        mock_booking.end_time = datetime.now(timezone.utc) + timedelta(hours=1)

        invalid_states = [
            bookings_service.BookingStatus.CONFIRMED,
            bookings_service.BookingStatus.ACTIVE,
            bookings_service.BookingStatus.COMPLETED,
            bookings_service.BookingStatus.CANCELLED
        ]
        
        for state in invalid_states:
            mock_booking.status = state
            with pytest.raises(ValueError, match="Bookings can only be confirmed from a requested state"):
                bookings_service.confirm_booking(mock_booking.id, mock_booking)


    def test_cancel_booking_cancels_requested_booking(self, bookings_service, sample_booking, mock_repository, mock_db, mock_notifications_public, mock_payments_public):
        """Test cancellation of requested booking"""
        #Set booking.status to REQUESTED
        #Set booking.start_time in future
        #Mock repository.update_booking
        #Mock notifications.booking_cancelled
        #Mock payments_public.void_escrow_for_booking
        #Call cancel_booking with booking
        #Verify status changed to CANCELLED
        #Verify void_escrow_for_booking called
        #Verify cancelled booking returned
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.REQUESTED
        mock_booking.start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        
        mock_repository.update_booking.return_value = mock_booking

        result = bookings_service.cancel_booking(mock_booking.id, mock_booking)

        assert result.status == bookings_service.BookingStatus.CANCELLED
        mock_notifications_public.booking_cancelled.assert_called_once_with(
            mock_booking.buyer, 
            mock_booking, 
            reason="user_cancelled"
        )
        mock_payments_public.void_escrow_for_booking.assert_called_once_with(booking=mock_booking)
        mock_repository.update_booking.assert_called_once_with(mock_db, mock_booking)
        assert result == mock_booking
        
    def test_cancel_booking_cancels_confirmed_booking(self, bookings_service, sample_booking, mock_repository, mock_payments_public, mock_db):
        """Test cancellation of confirmed booking before start time"""
        #Set booking.status to CONFIRMED
        #Set booking.start_time in future
        #Mock dependencies for successful cancellation
        #Call cancel_booking with booking
        #Verify status changed to CANCELLED
        #Verify void_escrow_for_booking called
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.CONFIRMED
        mock_booking.start_time = datetime.now(timezone.utc) + timedelta(hours=1)

        mock_repository.update_booking.return_value = mock_booking

        result = bookings_service.cancel_booking(mock_booking.id, mock_booking)
        
        assert result.status == bookings_service.BookingStatus.CANCELLED
        assert result == mock_booking
        mock_payments_public.void_escrow_for_booking.assert_called_once_with(booking=mock_booking)

    def test_cancel_booking_raises_error_when_listing_missing(self, bookings_service, sample_booking):
        """Test error when booking has no associated listing"""
        #Set booking.listing = None
        #Call cancel_booking with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.listing = None

        with pytest.raises(ValueError, match="Cannot cancel a booking without an associated listing"):
            bookings_service.cancel_booking(mock_booking.id, mock_booking)

    def test_cancel_booking_raises_error_after_start_time(self, bookings_service, sample_booking):
        """Test error when trying to cancel after booking start time"""
        #Set booking.start_time in the past
        #Call cancel_booking with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.start_time = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(ValueError, match="Cannot cancel booking after booking start_time"):
            bookings_service.cancel_booking(mock_booking.id, mock_booking)        

    def test_cancel_booking_raises_error_from_invalid_state(self, bookings_service, sample_booking):
        """Test error when cancelling from invalid state"""
        #Set booking.status to ACTIVE
        #Call cancel_booking with booking
        #Verify ValueError is raised
        #Repeat for COMPLETED and CANCELLED states
        mock_booking = sample_booking
        mock_booking.start_time = datetime.now(timezone.utc) + timedelta(hours=1)

        invalid_states = [
            bookings_service.BookingStatus.ACTIVE,
            bookings_service.BookingStatus.COMPLETED,
            bookings_service.BookingStatus.CANCELLED
        ]
        
        for state in invalid_states:
            mock_booking.status = state
            with pytest.raises(ValueError, match="Booking must be pending, requested, or confirmed in order to cancel."):
                bookings_service.cancel_booking(mock_booking.id, mock_booking)

    #def start_session(self, booking_id: UUID, booking: Booking | None = None):
    def test_start_session_activates_confirmed_booking(self, bookings_service, sample_booking, mock_repository, mock_credentials_public, mock_notifications_public):
        """Test starting session for confirmed booking within window"""
        #Set booking.status to CONFIRMED
        #Set current time within booking window
        #Set booking.active_session_start = None
        #Mock repository.update_booking
        #Mock notifications.booking_activated
        #Mock credentials_public.issue_for_booking
        #Call start_session with booking
        #Verify status changed to ACTIVE
        #Verify active_session_start set to current time
        #Verify credentials issued
        #Verify activated booking returned
        mock_booking = sample_booking
        mock_booking.start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_booking.end_time = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_booking.active_session_start = None
        mock_booking.status = bookings_service.BookingStatus.CONFIRMED

        mock_repository.update_booking.return_value = mock_booking

        result = bookings_service.start_session(mock_booking.id, mock_booking)

        assert result.status == bookings_service.BookingStatus.ACTIVE
        assert abs((result.active_session_start - datetime.now(timezone.utc)).total_seconds()) <= 3
        mock_credentials_public.issue_for_booking.assert_called_once_with(mock_booking)
        mock_notifications_public.booking_activated.assert_called_once_with(mock_booking.buyer, mock_booking)
        assert result == mock_booking


    def test_start_session_raises_error_when_listing_missing(self, bookings_service, sample_booking):
        """Test error when booking has no associated listing"""
        #Set booking.listing = None
        #Call start_session with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.listing = None

        with pytest.raises(ValueError, match="Listing not attached to booking"):
            bookings_service.start_session(mock_booking.id, mock_booking)

    def test_start_session_raises_error_from_wrong_state(self, bookings_service, sample_booking):
        """Test error when starting from non-confirmed state"""
        #Set booking.status to REQUESTED
        #Call start_session with booking
        #Verify ValueError is raised
        #Repeat for other invalid states
        mock_booking = sample_booking
        mock_booking.start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_booking.end_time = datetime.now(timezone.utc) + timedelta(hours=1)

        invalid_states = [
            bookings_service.BookingStatus.REQUESTED,
            bookings_service.BookingStatus.ACTIVE,
            bookings_service.BookingStatus.COMPLETED,
            bookings_service.BookingStatus.CANCELLED
        ]
        
        for state in invalid_states:
            mock_booking.status = state
            with pytest.raises(ValueError, match="Only a confirmed booking can be started."):
                bookings_service.start_session(mock_booking.id, mock_booking)


    def test_start_session_raises_error_when_already_started(self, bookings_service, sample_booking):
        """Test error when session already started"""
        #Set booking.active_session_start to a past time
        #Call start_session with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.CONFIRMED
        mock_booking.active_session_start = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(ValueError, match="Session already started"):
            bookings_service.start_session(mock_booking.id, mock_booking)

    def test_start_session_raises_error_outside_window(self, bookings_service, sample_booking):
        """Test error when starting outside booking window"""
        #Set current time before booking.start_time
        #Call start_session with booking
        #Verify ValueError is raised
        #Set current time after booking.end_time
        #Call start_session with booking
        #Verify ValueError is raised
        mock_booking = sample_booking

        mock_booking.active_session_start = None #set globally in previous test

        mock_booking.status = bookings_service.BookingStatus.CONFIRMED

        mock_booking.start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_booking.end_time = datetime.now(timezone.utc) + timedelta(hours=2)

        with pytest.raises(ValueError, match="Cannot start before booking start_time"):
            bookings_service.start_session(mock_booking.id, mock_booking)

        mock_booking.start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        mock_booking.end_time = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(ValueError, match="Cannot start; booking window expired"):
            bookings_service.start_session(mock_booking.id, mock_booking)
        

    def test_end_session_completes_active_booking(self, bookings_service, sample_booking, mock_repository, mock_db, mock_compliance_public, mock_notifications_public, mock_payments_public, mock_credentials_public):
        """Test ending session for active booking"""
        #Set booking.status to ACTIVE
        #Set booking.active_session_start to past time
        #Set booking.active_session_end = None
        #Mock calculate_price to return actual price
        #Mock compliance_public.simulate_wipe_for_booking
        #Mock compliance_public.require_attestation_for_booking
        #Mock repository.update_booking
        #Mock notifications.booking_completed
        #Mock payments_public.capture_for_booking
        #Mock credentials_public.revoke_for_booking
        #Call end_session with booking
        #Verify status changed to COMPLETED
        #Verify active_session_end set
        #Verify actual_price_charged calculated
        #Verify compliance methods called
        #Verify payment captured and credentials revoked
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.ACTIVE
        mock_booking.active_session_start = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_booking.active_session_end = None
        actual_price = 10
        
        bookings_service.calculate_price = Mock(return_value=actual_price)

        mock_repository.update_booking.return_value = mock_booking

        result = bookings_service.end_session(mock_booking.id, mock_booking)

        assert result.status == bookings_service.BookingStatus.COMPLETED
        assert result.active_session_end is not None
        assert result.actual_price_charged == actual_price
        assert result == mock_booking

        mock_compliance_public.simulate_wipe_for_booking.assert_called_once_with(mock_booking)
        mock_compliance_public.require_attestation_for_booking.assert_called_once_with(mock_booking)
        mock_notifications_public.booking_completed.assert_called_once_with(mock_booking.buyer, mock_booking)
        mock_payments_public.capture_for_booking.assert_called_once_with(booking=mock_booking)
        mock_credentials_public.revoke_for_booking(mock_booking)

    def test_end_session_raises_error_when_listing_missing(self, bookings_service, sample_booking):
        """Test error when booking has no associated listing"""
        #Set booking.listing = None
        #Call end_session with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.listing = None

        with pytest.raises(ValueError, match="Listing not attached to booking"):
            bookings_service.end_session(mock_booking.id, mock_booking)

    def test_end_session_raises_error_from_wrong_state(self, bookings_service, sample_booking):
        """Test error when ending from non-active state"""
        #Set booking.status to CONFIRMED
        #Call end_session with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.COMPLETED

        with pytest.raises(ValueError, match="Cannot end, current status is not active"):
            bookings_service.end_session(mock_booking.id, mock_booking)

    def test_end_session_raises_error_when_already_ended(self, bookings_service, sample_booking):
        """Test error when session already ended"""
        #Set booking.active_session_end to a past time
        #Call end_session with booking
        #Verify ValueError is raised
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.ACTIVE
        mock_booking.active_session_end = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(ValueError, match="Session already ended"):
            bookings_service.end_session(mock_booking.id, mock_booking)

    def test_get_org_bookings_in_period_delegates_to_repository(self, bookings_service, mock_repository, mock_db):
        """Test org bookings in period delegates to repository"""
        #Create org_id, period_start, period_end
        #Mock repository.list_bookings_for_org_in_period to return bookings
        #Call get_org_bookings_in_period with parameters
        #Verify repository method called with correct parameters
        #Verify bookings are returned
        org_id = uuid4()
        period_start = datetime.now(timezone.utc) - timedelta(days=10)
        period_end = datetime.now(timezone.utc) + timedelta(days=10)
        mock_bookings = [Mock(spec=Booking), Mock(spec=Booking)]

        mock_repository.list_bookings_for_org_in_period.return_value = mock_bookings

        result = bookings_service.get_org_bookings_in_period(org_id, period_start, period_end)
        
        mock_repository.list_bookings_for_org_in_period.assert_called_once_with(mock_db, org_id=org_id, period_start=period_start, period_end=period_end)
        
        assert result == mock_bookings
    
    #Cross-domain integration tests
    def test_request_booking_fails_when_escrow_fails(self, bookings_service, sample_booking_request, mock_payments_public, mock_repository, mock_db):
        """Test booking creation rolled back when escrow fails"""
        #Mock successful booking creation
        #Mock payments_public.escrow_for_booking to raise exception
        #Call request_booking with buyer_id and payload
        #Verify exception is propagated
        #Consider verifying no booking persists (transaction rollback)
        payload = sample_booking_request
        buyer_user_id = uuid4()
        start_utc = datetime.now(timezone.utc)
        end_utc = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_listing = Mock(spec=Listing)

        mock_booking = Mock(spec=Booking)
        mock_booking.total_price_estimate = 150.0
        mock_booking.status = bookings_service.BookingStatus.REQUESTED
        
        with patch.object(bookings_service, 'normalize_times', return_value=(start_utc, end_utc)) as mock_normalize, \
            patch.object(bookings_service, 'fetch_listing_or_raise', return_value=mock_listing) as mock_fetch, \
            patch.object(bookings_service, 'calculate_price', return_value=150.0) as mock_calc, \
            patch.object(bookings_service, 'build_booking_model', return_value=mock_booking) as mock_build:

            mock_repository.create_booking.return_value = mock_booking
            
            mock_payments_public.escrow_for_booking.side_effect = ValueError("Escrow failed")

            with pytest.raises(ValueError, match="Escrow failed"):
                bookings_service.request_booking(buyer_user_id, payload)
            
            mock_repository.create_booking.assert_called_once_with(mock_db, mock_booking)

            mock_payments_public.escrow_for_booking.assert_called_once()

    def test_start_session_fails_when_credential_issuance_fails(self, bookings_service, sample_booking, mock_credentials_public, mock_repository, mock_db):
        """Test session start rolled back when credential issuance fails"""
        #Mock successful state transition to ACTIVE
        #Mock credentials_public.issue_for_booking to raise exception
        #Call start_session with booking
        #Verify exception is propagated
        #Consider verifying booking state not changed
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.CONFIRMED
        mock_booking.active_session_start = None
        mock_booking.start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_booking.end_time = datetime.now(timezone.utc) + timedelta(hours=1)

        mock_repository.update_booking.return_value = mock_booking

        mock_credentials_public.issue_for_booking.side_effect = ValueError("Credentials issuance failed")

        with pytest.raises(ValueError, match="Credentials issuance failed"):
            bookings_service.start_session(mock_booking.id, mock_booking)
        
        mock_repository.update_booking.assert_called_once_with(mock_db, mock_booking)


    def test_end_session_fails_when_compliance_check_fails(self, bookings_service, sample_booking, mock_compliance_public, mock_payments_public):
        """Test session end fails when wipe attestation fails"""
        #Mock compliance_public.require_attestation_for_booking to raise exception
        #Call end_session with booking
        #Verify exception is propagated
        #Verify payment capture not called
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.ACTIVE
        mock_booking.active_session_end = None
        actual_price = 10

        bookings_service.calculate_price = Mock(return_value=actual_price)

        mock_compliance_public.require_attestation_for_booking.side_effect = ValueError("Wipe attestation generation failed")

        with pytest.raises(ValueError, match="Wipe attestation generation failed"):
            bookings_service.end_session(mock_booking.id, mock_booking)
        
        mock_payments_public.capture_for_booking.assert_not_called()

    def test_end_session_fails_when_payment_capture_fails(self, bookings_service, sample_booking, mock_payments_public, mock_credentials_public):
        """Test session end rolled back when payment capture fails"""
        #Mock successful compliance checks
        #Mock payments_public.capture_for_booking to raise exception
        #Call end_session with booking
        #Verify exception is propagated
        #Consider verifying credentials not revoked
        mock_booking = sample_booking
        mock_booking.status = bookings_service.BookingStatus.ACTIVE
        mock_booking.active_session_end = None
        actual_price = 10

        bookings_service.calculate_price = Mock(return_value=actual_price)

        mock_payments_public.capture_for_booking.side_effect = ValueError("Payment capture failed")

        with pytest.raises(ValueError, match="Payment capture failed"):
            bookings_service.end_session(mock_booking.id, mock_booking)
        
        mock_credentials_public.revoke_for_booking.assert_not_called()

    # #Edge cases and business rules
    # def test_request_booking_with_maximum_duration(self, bookings_service, sample_booking_request):
    #     """Test booking request with maximum allowed duration"""
    #     #Create booking request with 7-day duration (max)
    #     #Mock all dependencies for success
    #     #Call request_booking
    #     #Verify booking created successfully
    #     pass

    # def test_request_booking_exceeds_maximum_duration(self, bookings_service, sample_booking_request):
    #     """Test error when booking duration exceeds maximum"""
    #     #Create booking request with >7 day duration
    #     #Call request_booking
    #     #Verify ValueError is raised
    #     pass

    # def test_overlapping_bookings_prevention(self, bookings_service, sample_booking):
    #     """Test business rule preventing overlapping bookings"""
    #     #This test would require checking repository for existing bookings
    #     #Mock repository method to return overlapping booking
    #     #Call request_booking when overlapping exists
    #     #Verify ValueError is raised
    #     pass

    # def test_booking_state_machine_integrity(self, bookings_service, sample_booking):
    #     """Test all valid state transitions work correctly"""
    #     #Test REQUESTED -> CONFIRMED -> ACTIVE -> COMPLETED path
    #     #Test REQUESTED -> CANCELLED path
    #     #Test CONFIRMED -> CANCELLED path
    #     #Verify invalid transitions raise errors
    #     pass