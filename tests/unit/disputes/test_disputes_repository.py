import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.disputes.repository import DisputeRepository
from app.disputes.models import Dispute, DisputeStatus


@pytest.fixture
def mock_session():
    """Mock database session fixture"""
    return Mock()


@pytest.fixture
def dispute_repository(mock_session):
    """DisputeRepository instance fixture"""
    return DisputeRepository(mock_session)


@pytest.fixture
def sample_dispute():
    """Fixture for a mock dispute object"""
    dispute = Mock(spec=Dispute)
    dispute.id = uuid4()
    dispute.booking_id = uuid4()
    dispute.opened_by_user_id = uuid4()
    dispute.reason = "Service not as described"
    dispute.status = DisputeStatus.OPEN
    dispute.created_at = datetime.now(timezone.utc)
    dispute.resolution_notes = None
    dispute.resolved_at = None
    return dispute


class TestDisputeRepository:
    
    def test_create_dispute_performs_database_operations(self, dispute_repository, mock_session):
        """Test that dispute creation performs database operations"""
        booking_id = uuid4()
        user_id = uuid4()
        reason = "Service not as described"
        
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        result = dispute_repository.create_dispute(booking_id, user_id, reason)
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    def test_get_by_id_returns_dispute_when_exists(self, dispute_repository, mock_session, sample_dispute):
        """Test getting dispute by ID returns dispute"""
        dispute_id = uuid4()
        
        mock_stmt = Mock()
        mock_session.scalar.return_value = sample_dispute
        mock_session.select.return_value = mock_stmt
        
        result = dispute_repository.get_by_id(dispute_id)
        
        assert result == sample_dispute
        mock_session.scalar.assert_called_once()

    def test_get_by_id_returns_none_when_not_found(self, dispute_repository, mock_session):
        """Test getting dispute by ID returns None when not found"""
        dispute_id = uuid4()
        
        mock_session.scalar.return_value = None
        
        result = dispute_repository.get_by_id(dispute_id)
        
        assert result is None
        mock_session.scalar.assert_called_once()

    def test_list_for_user_returns_user_disputes_sorted(self, dispute_repository, mock_session):
        """Test getting disputes for a user returns sorted list"""
        user_id = uuid4()
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_session.scalars.return_value = mock_disputes
        
        result = dispute_repository.list_for_user(user_id)
        
        assert result == mock_disputes
        mock_session.scalars.assert_called_once()

    def test_list_for_user_returns_empty_list_when_none_exist(self, dispute_repository, mock_session):
        """Test getting disputes for user returns empty list when none exist"""
        user_id = uuid4()
        
        mock_session.scalars.return_value = []
        
        result = dispute_repository.list_for_user(user_id)
        
        assert result == []
        mock_session.scalars.assert_called_once()

    def test_list_for_booking_returns_booking_disputes_sorted(self, dispute_repository, mock_session):
        """Test getting disputes for a booking returns sorted list"""
        booking_id = uuid4()
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_session.scalars.return_value = mock_disputes
        
        result = dispute_repository.list_for_booking(booking_id)
        
        assert result == mock_disputes
        mock_session.scalars.assert_called_once()

    def test_list_for_booking_returns_empty_list_when_none_exist(self, dispute_repository, mock_session):
        """Test getting disputes for booking returns empty list when none exist"""
        booking_id = uuid4()
        
        mock_session.scalars.return_value = []
        
        result = dispute_repository.list_for_booking(booking_id)
        
        assert result == []
        mock_session.scalars.assert_called_once()

    def test_list_open_for_admin_returns_open_disputes_sorted(self, dispute_repository, mock_session):
        """Test getting open disputes for admin returns sorted list"""
        mock_disputes = [Mock(spec=Dispute), Mock(spec=Dispute)]
        
        mock_session.scalars.return_value = mock_disputes
        
        result = dispute_repository.list_open_for_admin()
        
        assert result == mock_disputes
        mock_session.scalars.assert_called_once()

    def test_list_open_for_admin_returns_empty_list_when_none_exist(self, dispute_repository, mock_session):
        """Test getting open disputes for admin returns empty list when none exist"""
        
        mock_session.scalars.return_value = []
        
        result = dispute_repository.list_open_for_admin()
        
        assert result == []
        mock_session.scalars.assert_called_once()

    def test_update_status_updates_existing_dispute(self, dispute_repository, mock_session, sample_dispute):
        """Test updating status for existing dispute"""
        dispute_id = uuid4()
        new_status = DisputeStatus.RESOLVED_REFUNDED
        resolution_notes = "Issue resolved with partial refund"
        resolved_at = datetime.now(timezone.utc)
        
        mock_stmt = Mock()
        mock_session.execute.return_value = None
        mock_session.commit.return_value = None
        
        # Mock get_by_id to return the dispute after update
        mock_session.scalar.return_value = sample_dispute
        mock_session.select.return_value = mock_stmt
        
        result = dispute_repository.update_status(
            dispute_id, new_status, resolution_notes, resolved_at
        )
        
        assert result == sample_dispute
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.scalar.assert_called_once()

    def test_update_status_returns_none_for_nonexistent_dispute(self, dispute_repository, mock_session):
        """Test updating status returns None for non-existent dispute"""
        dispute_id = uuid4()
        new_status = DisputeStatus.RESOLVED_DENIED
        
        mock_session.execute.return_value = None
        mock_session.commit.return_value = None
        mock_session.scalar.return_value = None
        
        result = dispute_repository.update_status(dispute_id, new_status)
        
        assert result is None
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.scalar.assert_called_once()