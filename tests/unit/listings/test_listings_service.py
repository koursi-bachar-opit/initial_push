import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.listings.service import ListingsService
from app.listings.repository import ListingsRepository
from app.listings.models import Listing
from app.listings.schemas import ListingCreate


@pytest.fixture
def mock_db():
    """Mock database session fixture"""
    return Mock()


@pytest.fixture
def mock_repository():
    """Mock ListingsRepository fixture"""
    return Mock(spec=ListingsRepository)


@pytest.fixture
def mock_machines_public():
    """Mock MachinesPublic fixture for machine ownership checks"""
    return Mock()


@pytest.fixture
def mock_providers_public():
    """Mock ProvidersPublic fixture for provider verification"""
    return Mock()


@pytest.fixture
def mock_metrics_public():
    """Mock MetricsPublic fixture for metrics collection"""
    return Mock()


@pytest.fixture
def mock_agent():
    """Mock ProviderAgentClient fixture for metrics collection"""
    return Mock()


@pytest.fixture
def listings_service(
    mock_db,
    mock_repository,
    mock_machines_public,
    mock_providers_public,
    mock_metrics_public,
    mock_agent
):
    """Main service fixture that composes all dependencies"""
    return ListingsService(
        db=mock_db,
        listing_repo=mock_repository,
        machines_public=mock_machines_public,
        providers_public=mock_providers_public,
        metrics_public=mock_metrics_public,
        agent=mock_agent
    )


@pytest.fixture
def sample_listing_data():
    """Fixture for sample listing creation data"""
    return ListingCreate(
        title="Test Listing",
        price=100.0,
        machine_id=uuid4()
    )


@pytest.fixture
def sample_listing():
    """Fixture for a mock listing object"""
    listing = Mock(spec=Listing)
    listing.id = uuid4()
    listing.title = "Test Listing"
    listing.price = 100.0
    listing.machine_id = uuid4()
    listing.machine = Mock()
    listing.machine.id = uuid4()
    listing.machine.provider_id = uuid4()
    return listing


class TestListingsService:
    #def create_listing(self, provider_id: UUID, payload: ListingCreate):
    def test_create_listing_successfully_creates_listing(
        self, listings_service, mock_db, mock_repository, 
        mock_machines_public, mock_providers_public, sample_listing_data
    ):
        """Test successful listing creation when provider owns machine"""
        #Mock providers_public.require_verified_provider to pass
        #Mock machines_public.provider_owns_machine to return True
        #Mock repository.create_listing to return a listing
        #Call service.create_listing with provider ID and listing data
        #Verify provider verification was called
        #Verify machine ownership check was called
        #Verify repository.create_listing was called with correct listing
        #Verify the created listing is returned
        mock_listing = Mock(spec=Listing)
        provider_id = uuid4()
        
        mock_providers_public.require_verified_provider.return_value = None
        mock_machines_public.provider_owns_machine.return_value = True
        mock_repository.create_listing.return_value = mock_listing
        
        result = listings_service.create_listing(provider_id, sample_listing_data)
        
        assert result == mock_listing
        mock_providers_public.require_verified_provider.assert_called_once_with(provider_id)
        mock_machines_public.provider_owns_machine.assert_called_once_with(
            provider_id, sample_listing_data.machine_id
        )
        mock_repository.create_listing.assert_called_once()
        
    def test_create_listing_raises_error_when_provider_not_verified(
        self, listings_service, mock_providers_public, sample_listing_data, mock_machines_public
    ):
        """Test error when provider is not verified"""
        #Mock providers_public.require_verified_provider to raise error
        #Call service.create_listing with unverified provider ID
        #Verify error is raised and machine ownership check is NOT called
        provider_id = uuid4()
        mock_providers_public.require_verified_provider.side_effect = ValueError("Provider not verified")

        with pytest.raises(ValueError, match="Provider not verified"):
            listings_service.create_listing(provider_id, sample_listing_data)

        mock_providers_public.require_verified_provider.assert_called_once_with(provider_id)
        mock_machines_public.provider_owns_machine.assert_not_called()

    def test_create_listing_raises_error_when_not_machine_owner(
        self, listings_service, mock_providers_public, 
        mock_machines_public, sample_listing_data, mock_repository
    ):
        """Test error when provider doesn't own the machine"""
        #Mock providers_public.require_verified_provider to pass
        #Mock machines_public.provider_owns_machine to return False
        #Call service.create_listing with provider who doesn't own machine
        #Verify ValueError is raised with correct message
        #Verify repository.create_listing is NOT called
        provider_id = uuid4()
        
        mock_providers_public.require_verified_provider.return_value = None
        mock_machines_public.provider_owns_machine.return_value = False
        
        with pytest.raises(ValueError, match="You must own this machine."):
            listings_service.create_listing(provider_id, sample_listing_data)
        
        mock_providers_public.require_verified_provider.assert_called_once_with(provider_id)
        mock_machines_public.provider_owns_machine.assert_called_once_with(
            provider_id, sample_listing_data.machine_id
        )
        mock_repository.create_listing.assert_not_called()

    #def get_listing_by_id(self, listing_id: UUID) -> Listing | None:
    def test_get_listing_by_id_returns_listing_when_exists(
        self, listings_service, mock_db, mock_repository
    ):
        """Test successful listing retrieval by ID"""
        #Mock repository.get_listing_by_id to return a listing
        #Call service.get_listing_by_id with listing UUID
        #Verify repository method was called with correct ID
        #Verify the listing is returned
        mock_listing = Mock(spec=Listing)
        listing_id = uuid4()

        mock_repository.get_listing_by_id.return_value = mock_listing
        result = listings_service.get_listing_by_id(listing_id)

        assert result == mock_listing
        mock_repository.get_listing_by_id.assert_called_once_with(mock_db, listing_id)

    def test_get_listing_by_id_returns_none_when_not_found(
        self, listings_service, mock_db, mock_repository
    ):
        """Test retrieving non-existent listing returns None"""
        #Mock repository.get_listing_by_id to return None
        #Call service.get_listing_by_id with listing UUID
        #Verify None is returned
        listing_id = uuid4()

        mock_repository.get_listing_by_id.return_value = None

        result = listings_service.get_listing_by_id(listing_id)
        assert result == None

    #def search_listings_by_name(self, name: str):
    def test_search_listings_by_name_returns_listings_with_metrics(
        self, listings_service, mock_db, mock_repository, 
        mock_metrics_public, mock_agent, sample_listing
    ):
        """Test search returns listings with metrics data"""
        #Mock repository.search_by_title to return list of listings
        #Mock agent.collect_metrics_raw for each listing's machine
        #Mock metrics_public.ingest_raw_metrics for each listing
        #Mock metrics_public.get_latest_metrics for each listing
        #Call service.search_listings_by_name with search term
        #Verify each listing gets metrics collected and ingested
        #Verify result includes listings with latest_metrics
        search_term = "title"
        
        mock_listing1 = Mock(spec=Listing)
        mock_listing1.machine = Mock()
        mock_listing1.machine.id = uuid4()
        mock_listing1.machine.provider_id = uuid4()
        
        mock_listing2 = Mock(spec=Listing)
        mock_listing2.machine = Mock()
        mock_listing2.machine.id = uuid4()
        mock_listing2.machine.provider_id = uuid4()
        
        mock_listings = [mock_listing1, mock_listing2]
        mock_repository.search_by_title.return_value = mock_listings
        
        mock_raw_metrics = {"cpu": 80}
        mock_latest_metrics = {"cpu": 85}
        
        mock_agent.collect_metrics_raw.return_value = mock_raw_metrics
        mock_metrics_public.get_latest_metrics.return_value = mock_latest_metrics

        results = listings_service.search_listings_by_name(search_term)
        
        assert len(results) == 2
        assert results[0]["listing"] == mock_listing1
        assert results[0]["latest_metrics"] == mock_latest_metrics
        assert results[1]["listing"] == mock_listing2
        assert results[1]["latest_metrics"] == mock_latest_metrics

        assert mock_agent.collect_metrics_raw.call_count == 2
        assert mock_metrics_public.ingest_raw_metrics.call_count == 2
        assert mock_metrics_public.get_latest_metrics.call_count == 2


    def test_search_listings_by_name_returns_empty_when_no_matches(
        self, listings_service, mock_db, mock_repository, mock_agent, mock_metrics_public
    ):
        """Test search returns empty when no listings match"""
        #Mock repository.search_by_title to return empty list
        #Call service.search_listings_by_name with search term
        #Verify empty list is returned
        #Verify agent and metrics methods are NOT called
        search_term = "title"

        mock_repository.search_by_title.return_value = []

        result = listings_service.search_listings_by_name(search_term)
        assert result == []
        mock_repository.search_by_title.assert_called_once_with(mock_db, search_term)
        mock_agent.collect_metrics_raw.assert_not_called()
        mock_metrics_public.ingest_raw_metrics.assert_not_called()
        mock_metrics_public.get_latest_metrics.assert_not_called()

    #def _collect_listing_metrics(self, listing: Listing):
    def test_collect_listing_metrics_collects_and_ingests_metrics(
        self, listings_service, mock_metrics_public, mock_agent, sample_listing
    ):
        """Test metrics collection for a single listing"""
        #Mock agent.collect_metrics_raw to return raw metrics
        #Mock metrics_public.ingest_raw_metrics to return success
        #Mock metrics_public.get_latest_metrics to return metrics data
        #Call service._collect_listing_metrics with a listing
        #Verify agent.collect_metrics_raw called with machine ID
        #Verify metrics_public.ingest_raw_metrics called with correct params
        #Verify metrics_public.get_latest_metrics called with machine ID
        #Verify latest metrics are returned
        mock_raw_metrics = {"cpu": 80}
        mock_latest_metrics = {"cpu": 85}
        
        mock_agent.collect_metrics_raw.return_value = mock_raw_metrics
        mock_metrics_public.get_latest_metrics.return_value = mock_latest_metrics
        
        result = listings_service._collect_listing_metrics(sample_listing)
        
        assert result == mock_latest_metrics
        mock_agent.collect_metrics_raw.assert_called_once_with(sample_listing.machine.id)
        mock_metrics_public.ingest_raw_metrics.assert_called_once_with(
            machine_id=sample_listing.machine.id,
            raw=mock_raw_metrics,
            provider_id=sample_listing.machine.provider_id
        )
        mock_metrics_public.get_latest_metrics.assert_called_once_with(sample_listing.machine.id)

    #def list_listings(self):
    def test_list_listings_delegates_to_repository(
        self, listings_service, mock_db, mock_repository
    ):
        """Test listing retrieval delegates to repository"""
        #Mock repository.get_listings to return list of listings
        #Call service.list_listings
        #Verify repository.get_listings was called
        #Verify the listings are returned
        mock_listings = [Mock(spec=Listing), Mock(spec=Listing)]

        mock_repository.get_listings.return_value = mock_listings

        result = listings_service.list_listings()

        assert result == mock_listings
        mock_repository.get_listings.assert_called_once_with(mock_db)