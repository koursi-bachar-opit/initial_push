# import pytest
# from unittest.mock import Mock
# from uuid import uuid4

# from app.listings.repository import ListingsRepository
# from app.listings.models import Listing


# @pytest.fixture
# def mock_db():
#     """Mock database session fixture"""
#     return Mock()


# @pytest.fixture
# def listing_repository():
#     """ListingsRepository instance fixture"""
#     return ListingsRepository()


# @pytest.fixture
# def sample_listing():
#     """Fixture for a mock listing object"""
#     listing = Mock(spec=Listing)
#     listing.id = uuid4()
#     listing.title = "Test Listing"
#     listing.price = 100.0
#     listing.machine_id = uuid4()
#     return listing


# class TestListingsRepository:

#     #def get_listings(self, db: Session):
#     def test_get_listings_returns_all_listings_sorted(self, mock_db, listing_repository):
#         """Test getting all listings returns sorted list"""
#         #Mock db.query().order_by().all() to return a list of listings
#         #Call get_listings with mock db
#         #Verify the query chain includes order_by with Listing.id.asc()
#         #Verify the list of listings is returned
#         mock_listings = [Mock(spec=Listing), Mock(spec=Listing)]
        
#         #Mock the query chain: db.query(Listing).order_by(Listing.id.asc()).all()
#         mock_query = mock_db.query.return_value
#         mock_ordered_query = mock_query.order_by.return_value
#         mock_ordered_query.all.return_value = mock_listings
        
#         result = listing_repository.get_listings(mock_db)
        
#         assert result == mock_listings
#         mock_db.query.assert_called_once_with(Listing)
#         mock_query.order_by.assert_called_once()
#         mock_ordered_query.all.assert_called_once()

#     #def create_listing(self, db: Session, listing: Listing) -> Listing:
#     def test_create_listing_performs_database_operations(self, mock_db, listing_repository, sample_listing):
#         """Test that listing creation performs database operations"""
#         #Mock the database session
#         #Call create_listing with a listing object
#         #Verify db.add, db.commit, db.refresh were called with the listing
#         #Verify the listing is returned
#         result = listing_repository.create_listing(mock_db, sample_listing)
        
#         assert result == sample_listing
#         mock_db.add.assert_called_once_with(sample_listing)
#         mock_db.commit.assert_called_once()
#         mock_db.refresh.assert_called_once_with(sample_listing)

#     #def get_listing_by_id(self, db: Session, listing_id: UUID) -> Listing | None:
#     def test_get_listing_by_id_returns_listing_when_exists(self, mock_db, listing_repository):
#         """Test retrieving an existing listing by ID"""
#         #Mock db.get(Listing, listing_id) to return a listing
#         #Call get_listing_by_id with a UUID
#         #Verify the correct listing is returned
#         listing_id = uuid4()
#         mock_listing = Mock(spec=Listing)
        
#         mock_db.get.return_value = mock_listing
        
#         result = listing_repository.get_listing_by_id(mock_db, listing_id)
        
#         assert result == mock_listing
#         mock_db.get.assert_called_once_with(Listing, listing_id)

#     def test_get_listing_by_id_returns_none_when_not_found(self, mock_db, listing_repository):
#         """Test retrieving a non-existent listing returns None"""
#         #Mock db.get(Listing, listing_id) to return None
#         #Call get_listing_by_id with a UUID
#         #Verify None is returned
#         listing_id = uuid4()
        
#         mock_db.get.return_value = None
        
#         result = listing_repository.get_listing_by_id(mock_db, listing_id)
        
#         assert result is None
#         mock_db.get.assert_called_once_with(Listing, listing_id)

#     #def search_by_title(self, db: Session, name: str):
#     def test_search_by_title_returns_matching_listings(self, mock_db, listing_repository):
#         """Test search returns listings matching name or description"""
#         #Mock the complex query chain with or_() and ilike() filters
#         #Call search_by_title with a search term
#         #Verify the query includes correct filters and ordering
#         #Verify the matching listings are returned
#         search_term = "test"
#         mock_listings = [Mock(spec=Listing), Mock(spec=Listing)]
        
#         #Mock the complex query chain:
#         #db.query(Listing).filter(or_(...)).order_by(Listing.name.asc()).all()
#         mock_query = mock_db.query.return_value
#         mock_filtered_query = mock_query.filter.return_value
#         mock_ordered_query = mock_filtered_query.order_by.return_value
#         mock_ordered_query.all.return_value = mock_listings
        
#         result = listing_repository.search_by_title(mock_db, search_term)
        
#         assert result == mock_listings
#         mock_db.query.assert_called_once_with(Listing)
#         mock_query.filter.assert_called_once()
#         mock_filtered_query.order_by.assert_called_once()
#         mock_ordered_query.all.assert_called_once()

#     def test_search_by_title_returns_empty_list_for_empty_search(self, mock_db, listing_repository):
#         """Test search returns empty list for empty or whitespace search term"""
#         #Call search_by_title with empty string
#         #Verify empty list is returned without executing query
#         #Call search_by_title with whitespace-only string
#         #Verify empty list is returned without executing query
#         result_empty = listing_repository.search_by_title(mock_db, "")
#         result_whitespace = listing_repository.search_by_title(mock_db, "   ")
        
#         assert result_empty == []
#         assert result_whitespace == []
#         #Should not call database query methods
#         mock_db.query.assert_not_called()

#     def test_search_by_title_handles_none_search_term(self, mock_db, listing_repository):
#         """Test search handles None search term gracefully"""
#         #Call search_by_title with None
#         #Verify empty list is returned without executing query
#         result = listing_repository.search_by_title(mock_db, None)
        
#         assert result == []
#         mock_db.query.assert_not_called()