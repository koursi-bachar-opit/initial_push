# import pytest
# from unittest.mock import Mock
# from uuid import uuid4
# from fastapi import HTTPException

# from app.compliance.service import ComplianceService
# from app.compliance.repository import ComplianceRepository
# from app.compliance.models import WipeAttestation, WipeReviewStatus
# from app.compliance.schemas import WipeAttestationCreate, WipeAttestationUpdateStatus
# from app.machines.public import MachinesPublic
# from app.providers.public import ProvidersPublic
# from app.notifications.public import NotificationsPublic


# @pytest.fixture
# def mock_db():
#     """Mock database session fixture"""
#     return Mock()


# @pytest.fixture
# def mock_repository():
#     """Mock ComplianceRepository fixture"""
#     return Mock(spec=ComplianceRepository)


# @pytest.fixture
# def mock_machines_public():
#     """Mock MachinesPublic fixture"""
#     return Mock(spec=MachinesPublic)


# @pytest.fixture
# def mock_providers_public():
#     """Mock ProvidersPublic fixture"""
#     return Mock(spec=ProvidersPublic)


# @pytest.fixture
# def mock_notifications_public():
#     """Mock NotificationsPublic fixture"""
#     return Mock(spec=NotificationsPublic)


# @pytest.fixture
# def compliance_service(mock_db, mock_repository, mock_machines_public, mock_providers_public, mock_notifications_public):
#     """ComplianceService fixture with all dependencies"""
#     return ComplianceService(
#         db=mock_db,
#         repo=mock_repository,
#         machines_public=mock_machines_public,
#         providers_public=mock_providers_public,
#         notifications_public=mock_notifications_public
#     )


# @pytest.fixture
# def sample_booking():
#     """Fixture for a mock booking object"""
#     booking = Mock()
#     booking.id = uuid4()
#     booking.listing = Mock()
#     booking.listing.machine = Mock()
#     return booking


# @pytest.fixture
# def sample_machine():
#     """Fixture for a mock machine object"""
#     machine = Mock()
#     machine.id = uuid4()
#     machine.provider_id = uuid4()
#     return machine


# @pytest.fixture
# def sample_attestation():
#     """Fixture for a mock attestation object"""
#     attestation = Mock(spec=WipeAttestation)
#     attestation.id = uuid4()
#     attestation.booking_id = uuid4()
#     attestation.machine_id = uuid4()
#     attestation.method = "full_disk_wipe"
#     attestation.evidence_uri = "https://example.com/evidence.pdf"
#     attestation.notes = "Wipe completed successfully"
#     attestation.attested_at = Mock()
#     attestation.status = WipeReviewStatus.PENDING
#     return attestation


# @pytest.fixture
# def sample_attestation_create_data():
#     """Fixture for sample attestation creation data"""
#     return WipeAttestationCreate(
#         booking_id=uuid4(),
#         machine_id=uuid4(),
#         method="full_disk_wipe",
#         evidence_uri="https://example.com/evidence.pdf",
#         notes="Wipe completed successfully"
#     )


# @pytest.fixture
# def sample_attestation_update_data():
#     """Fixture for sample attestation update data"""
#     return WipeAttestationUpdateStatus(
#         status=WipeReviewStatus.VERIFIED,
#     )


# class TestComplianceService:
#     def test_simulate_wipe_for_booking_creates_new_attestation(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation, sample_machine):
#         """Test successful simulated wipe attestation creation when none exists"""
#         # Mock repository.get_by_booking to return None (no existing attestation)
#         # Mock booking.listing.machine to return a machine
#         # Mock repository.create to return attestation
#         # Call service.simulate_wipe_for_booking with booking
#         # Verify repository.get_by_booking was called with booking ID
#         # Verify repository.create was called with correct parameters
#         # Verify the created attestation is returned
#         mock_repository.get_by_booking.return_value = None
#         sample_booking.listing.machine = sample_machine
#         mock_repository.create.return_value = sample_attestation

#         result = compliance_service.simulate_wipe_for_booking(sample_booking)

#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)
#         mock_repository.create.assert_called_once_with(
#             db=mock_db,
#             booking_id=sample_booking.id,
#             machine_id=sample_machine.id,
#             method="simulated-secure-erase",
#             evidence_uri=f"mock://wipe/{sample_booking.id}.log",
#             notes="Simulated wipe completed successfully."
#         )
#         assert result == sample_attestation

#     def test_simulate_wipe_for_booking_returns_existing_attestation(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation):
#         """Test simulated wipe returns existing attestation when already exists"""
#         # Mock repository.get_by_booking to return existing attestation
#         # Call service.simulate_wipe_for_booking with booking
#         # Verify repository.get_by_booking was called with booking ID
#         # Verify repository.create is NOT called
#         # Verify existing attestation is returned
#         mock_repository.get_by_booking.return_value = sample_attestation

#         result = compliance_service.simulate_wipe_for_booking(sample_booking)

#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)
#         mock_repository.create.assert_not_called()
#         assert result == sample_attestation

#     def test_require_attestation_for_booking_returns_existing_attestation(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation):
#         """Test require_attestation returns attestation when exists"""
#         # Mock repository.get_by_booking to return attestation
#         # Call service.require_attestation_for_booking with booking
#         # Verify repository.get_by_booking was called with booking ID
#         # Verify attestation is returned (no exception raised)
#         mock_repository.get_by_booking.return_value = sample_attestation

#         result = compliance_service.require_attestation_for_booking(sample_booking)

#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)
#         assert result == sample_attestation

#     def test_require_attestation_for_booking_raises_error_when_not_found(self, compliance_service, mock_db, mock_repository, sample_booking):
#         """Test require_attestation raises HTTPException when no attestation exists"""
#         # Mock repository.get_by_booking to return None
#         # Call service.require_attestation_for_booking with booking
#         # Verify HTTPException is raised with correct status code and message
#         # Verify repository.get_by_booking was called with booking ID
#         mock_repository.get_by_booking.return_value = None

#         with pytest.raises(HTTPException, match="Booking cannot be completed until a wipe attestation exists."):
#             compliance_service.require_attestation_for_booking(sample_booking)

#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)

#     def test_submit_attestation_successfully_creates_for_owned_machine(self, compliance_service, mock_db, mock_repository, mock_machines_public, sample_attestation_create_data, sample_machine, sample_attestation):
#         """Test successful attestation submission by machine owner"""
#         # Mock machines_public.get_machine to return machine
#         # Set machine.provider_id to match provider_id parameter
#         # Mock repository.get_by_booking to return None (no existing attestation)
#         # Mock repository.create to return attestation
#         # Call service.submit_attestation with provider_id and create data
#         # Verify machines_public.get_machine was called with machine_id
#         # Verify repository.get_by_booking was called with booking_id
#         # Verify repository.create was called with correct parameters
#         # Verify attestation is returned
#         provider_id = uuid4()
#         mock_machines_public.get_machine.return_value = sample_machine
#         sample_machine.provider_id = provider_id
#         mock_repository.get_by_booking.return_value = None
#         mock_repository.create.return_value = sample_attestation

#         result = compliance_service.submit_attestation(provider_id, sample_attestation_create_data)

#         mock_machines_public.get_machine.assert_called_once_with(sample_attestation_create_data.machine_id)
#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_attestation_create_data.booking_id)
#         mock_repository.create.assert_called_once_with(
#             db=mock_db,
#             booking_id=sample_attestation_create_data.booking_id,
#             machine_id=sample_attestation_create_data.machine_id,
#             method=sample_attestation_create_data.method,
#             evidence_uri=sample_attestation_create_data.evidence_uri,
#             notes=sample_attestation_create_data.notes
#         )
#         assert result == sample_attestation

#     def test_submit_attestation_raises_error_when_machine_not_found(self, compliance_service, mock_machines_public, sample_attestation_create_data, mock_repository):
#         """Test attestation submission fails when machine doesn't exist"""
#         # Mock machines_public.get_machine to return None
#         # Call service.submit_attestation with provider_id and create data
#         # Verify HTTPException is raised with 404 status
#         # Verify repository.create is NOT called
#         provider_id = uuid4()
#         mock_machines_public.get_machine.return_value = None

#         with pytest.raises(HTTPException, match="Machine not found") as exception_info:
#             compliance_service.submit_attestation(provider_id, sample_attestation_create_data)

#         assert exception_info.value.status_code == 404
#         mock_repository.create.assert_not_called()

#     def test_submit_attestation_raises_error_when_not_machine_owner(self, compliance_service, mock_machines_public, sample_attestation_create_data, sample_machine, mock_repository):
#         """Test attestation submission fails when provider doesn't own machine"""
#         # Mock machines_public.get_machine to return machine
#         # Set machine.provider_id different from provider_id parameter
#         # Call service.submit_attestation with provider_id and create data
#         # Verify HTTPException is raised with 403 status
#         # Verify repository.create is NOT called
#         other_provider_id = uuid4()
#         provider_id = uuid4()
#         sample_machine.provider_id = provider_id
#         mock_machines_public.get_machine.return_value = sample_machine

#         with pytest.raises(HTTPException, match="You do not own this machine") as exception_info:
#             compliance_service.submit_attestation(other_provider_id, sample_attestation_create_data)

#         assert exception_info.value.status_code == 403
#         mock_repository.create.assert_not_called()

#     def test_submit_attestation_raises_error_when_attestation_already_exists(self, compliance_service, mock_repository, mock_machines_public, sample_attestation_create_data, sample_machine, sample_attestation):
#         """Test attestation submission fails when attestation already exists for booking"""
#         # Mock machines_public.get_machine to return machine
#         # Set machine.provider_id to match provider_id parameter
#         # Mock repository.get_by_booking to return existing attestation
#         # Call service.submit_attestation with provider_id and create data
#         # Verify HTTPException is raised with 400 status and correct message
#         # Verify repository.create is NOT called
#         provider_id = uuid4()
#         sample_machine.provider_id = provider_id
#         mock_machines_public.get_machine.return_value = sample_machine
#         mock_repository.get_by_booking.return_value = sample_attestation

#         with pytest.raises(HTTPException, match="Wipe attestation already exists for this booking") as exception_info:
#             compliance_service.submit_attestation(provider_id, sample_attestation_create_data)

#         assert exception_info.value.status_code == 400
#         mock_repository.create.assert_not_called()

#     def test_admin_review_successfully_updates_attestation(self, compliance_service, mock_db, mock_repository, sample_attestation, sample_attestation_update_data):
#         """Test successful admin review and status update"""
#         # Mock repository.update_status to return updated attestation
#         # Call service.admin_review with attestation_id and update data
#         # Verify repository.update_status was called with correct parameters
#         # Verify updated attestation is returned
#         attestation_id = uuid4()
#         mock_repository.update_status.return_value = sample_attestation

#         result = compliance_service.admin_review(attestation_id, sample_attestation_update_data)

#         mock_repository.update_status.assert_called_once_with(mock_db, attestation_id, sample_attestation_update_data.status)
#         assert result == sample_attestation

#     def test_admin_review_raises_error_when_attestation_not_found(self, compliance_service, mock_repository, sample_attestation_update_data):
#         """Test admin review raises error when attestation doesn't exist"""
#         # Mock repository.update_status to return None
#         # Call service.admin_review with attestation_id and update data
#         # Verify HTTPException is raised with 404 status
#         attestation_id = uuid4()
#         mock_repository.update_status.return_value = None

#         with pytest.raises(HTTPException, match="Attestation not found") as exception_info:
#             compliance_service.admin_review(attestation_id, sample_attestation_update_data)   

#         assert exception_info.value.status_code == 404 

#     def test_get_attestation_by_booking_delegates_to_repository(self, compliance_service, mock_db, mock_repository, sample_booking, sample_attestation):
#         """Test getting attestation by booking delegates to repository"""
#         # Mock repository.get_by_booking to return attestation
#         # Call service.get_attestation_by_booking with booking
#         # Verify repository.get_by_booking was called with booking ID
#         # Verify attestation is returned
#         mock_repository.get_by_booking.return_value = sample_attestation

#         result = compliance_service.get_attestation_by_booking(sample_booking)

#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)
#         assert result == sample_attestation

#     def test_get_attestation_by_booking_returns_none_when_not_found(self, compliance_service, mock_db, mock_repository, sample_booking):
#         """Test getting attestation by booking returns None when not found"""
#         # Mock repository.get_by_booking to return None
#         # Call service.get_attestation_by_booking with booking
#         # Verify None is returned
#         # Verify repository.get_by_booking was called with booking ID
#         mock_repository.get_by_booking.return_value = None

#         result = compliance_service.get_attestation_by_booking(sample_booking)

#         assert result is None
#         mock_repository.get_by_booking.assert_called_once_with(mock_db, sample_booking.id)

#     def test_list_machine_attestations_delegates_to_repository(self, compliance_service, mock_db, mock_repository):
#         """Test listing machine attestations delegates to repository"""
#         # Create machine_id
#         # Mock repository.list_machine_attestations to return list
#         # Call service.list_machine_attestations with machine_id
#         # Verify repository.list_machine_attestations was called with machine_id
#         # Verify list is returned
#         machine_id = uuid4()
#         sample_attestations = [Mock(spec=WipeAttestation), Mock(spec=WipeAttestation)]
#         mock_repository.list_machine_attestations.return_value = sample_attestations

#         result = compliance_service.list_machine_attestations(machine_id)

#         mock_repository.list_machine_attestations.assert_called_once_with(mock_db, machine_id)
#         assert result == sample_attestations

#     def test_list_machine_attestations_returns_empty_list_when_none_exist(self, compliance_service, mock_db, mock_repository):
#         """Test listing machine attestations returns empty list when none exist"""
#         # Mock repository.list_machine_attestations to return empty list
#         # Call service.list_machine_attestations with machine_id
#         # Verify empty list is returned
#         # Verify repository.list_machine_attestations was called
#         machine_id = uuid4()
#         mock_repository.list_machine_attestations.return_value = []

#         result = compliance_service.list_machine_attestations(machine_id)

#         mock_repository.list_machine_attestations.assert_called_once_with(mock_db, machine_id)
#         assert result == []

#     def test_list_all_attestations_delegates_to_repository(self, compliance_service, mock_db, mock_repository):
#         """Test listing all attestations delegates to repository"""
#         # Mock repository.list_all to return list
#         # Call service.list_all_attestations
#         # Verify repository.list_all was called
#         # Verify list is returned
#         sample_attestations = [Mock(spec=WipeAttestation), Mock(spec=WipeAttestation)]
#         mock_repository.list_all.return_value = sample_attestations

#         result = compliance_service.list_all_attestations()

#         mock_repository.list_all.assert_called_once_with(mock_db)
#         assert result == sample_attestations

#     def test_list_all_attestations_returns_empty_list_when_none_exist(self, compliance_service, mock_db, mock_repository):
#         """Test listing all attestations returns empty list when none exist"""
#         # Mock repository.list_all to return empty list
#         # Call service.list_all_attestations
#         # Verify empty list is returned
#         # Verify repository.list_all was called
#         mock_repository.list_all.return_value = []

#         result = compliance_service.list_all_attestations()

#         mock_repository.list_all.assert_called_once_with(mock_db)
#         assert result == []