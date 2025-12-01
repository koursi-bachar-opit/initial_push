import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.machines.service import MachinesService
from app.machines.repository import MachinesRepository
from app.machines.models import Machine
from app.machines.schemas import MachineCreate

from app.machines.schemas import MachineBenchmarkCreate

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_repository():
    return Mock(spec=MachinesRepository)

@pytest.fixture
def mock_benchmarks_public():
    return Mock()

@pytest.fixture
def machines_service(mock_db, mock_repository, mock_benchmarks_public):
    """Main service fixture that composes other fixtures"""
    return MachinesService(
        db=mock_db,
        machine_repo=mock_repository,
        providers_public=Mock(),
        benchmarks_public=mock_benchmarks_public
    )

@pytest.fixture
def sample_machine_data():
    """Fixture for sample machine creation data"""
    return MachineCreate(
        provider_id=uuid4(),
        hostname="test-machine",
        location_region="us-west",
        gpu_model="RTX 4090",
        gpu_count=1,
        vram_gb=24,
        cpu_model="Intel i9",
        cpu_cores=8,
        ram_gb=16,
        storage_gb=500,
        network_mbps=1000,
        notes="Test machine"
    )

@pytest.fixture
def sample_benchmark_data():
    """Fixture for sample benchmark creation data"""
    return MachineBenchmarkCreate(
        name="Test Score",
        score="4311",
        methodology_uri="machine-log-retrieval",
        artifact_uri="logs.machine.logger",
    )

class TestMachinesService:
    #def get_machine(self, machine_id: UUID) -> Machine:
    def test_get_machine_returns_machine_when_exists(self, machines_service, mock_db, mock_repository):
        """Test successful machine retrieval"""
        #Mock repository.get_machine to return a machine
        #Call service.get_machine with UUID
        #Verify the machine is returned
        mock_existing_machine = Mock(spec=Machine)
        machine_id = uuid4()
        
        mock_repository.get_machine.return_value = mock_existing_machine
        
        result = machines_service.get_machine(machine_id)
        
        assert result == mock_existing_machine
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)

    def test_get_machine_raises_error_when_not_found(self, machines_service, mock_db, mock_repository):
        """Test error when machine doesn't exist"""
        #Mock repository.get_machine to return None
        #Call service.get_machine with UUID
        #Verify ValueError is raised with correct message
        machine_id = uuid4()

        mock_repository.get_machine.return_value = None

        with pytest.raises(ValueError, match="Machine does not exist."):
            machines_service.get_machine(machine_id)
        
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)

    #def list_machines_for_provider(self, provider_id: UUID) -> list[Machine]:
    def test_list_machines_for_provider_delegates_to_repository(self, machines_service, mock_db, mock_repository):
        """Test listing machines delegates to repository"""
        #Mock repository.list_machines_for_provider to return machines
        #Call service.list_machines_for_provider with provider UUID
        #Verify repository method was called and result returned
        mock_machines = [Mock(spec=Machine), Mock(spec=Machine)]
        provider_id = uuid4()

        mock_repository.list_machines_for_provider.return_value = mock_machines

        result = machines_service.list_machines_for_provider(provider_id)

        assert result == mock_machines
        mock_repository.list_machines_for_provider.assert_called_once_with(mock_db, provider_id)

    #def create_machine(self, payload: MachineCreate) -> Machine:
    def test_create_machine_delegates_to_repository(self, machines_service, mock_db, mock_repository, sample_machine_data):
        """Test machine creation delegates to repository"""
        #Mock repository.create_machine to return a machine
        #Call service.create_machine with MachineCreate payload
        #Verify repository method was called and result returned
        mock_machine = Mock(spec=Machine)
        
        mock_repository.create_machine.return_value = mock_machine
        
        result = machines_service.create_machine(sample_machine_data)
        
        assert result == mock_machine
        mock_repository.create_machine.assert_called_once_with(mock_db, sample_machine_data)

    #def delete_machine(self, machine_id: UUID, provider_id: UUID):
    def test_delete_machine_successfully_deletes_owned_machine(self, machines_service, mock_db, mock_repository):
        """Test successful deletion when provider owns machine"""
        #Mock repository.get_machine to return owned machine
        #Mock repository.delete_machine
        #Call service.delete_machine with owner's provider_id
        #Verify repository.delete_machine was called with the machine
        owner_id = uuid4()
        machine_id = uuid4()
        mock_machine = Mock(spec=Machine)
        mock_machine.provider_id = owner_id

        mock_repository.get_machine.return_value = mock_machine

        machines_service.delete_machine(machine_id, owner_id)

        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)
        mock_repository.delete_machine.assert_called_once_with(mock_db, mock_machine)


    def test_delete_machine_raises_error_when_machine_not_found(self, machines_service, mock_db, mock_repository):
        """Test error when deleting non-existent machine"""
        #Mock repository.get_machine to return None
        #Call service.delete_machine
        #Verify ValueError is raised
        machine_id = uuid4()
        provider_id = uuid4()

        mock_repository.get_machine.return_value = None

        with pytest.raises(ValueError, match="Machine does not exist."):
            machines_service.delete_machine(machine_id, provider_id)
        
        mock_repository.delete_machine.assert_not_called()

    def test_delete_machine_raises_error_when_not_owner(self, machines_service, mock_db, mock_repository):
        """Test error when provider doesn't own machine"""
        #Mock repository.get_machine to return machine with different owner
        #Call service.delete_machine with different provider_id
        #Verify ValueError is raised
        owner_a_id = uuid4()
        owner_b_id = uuid4()
        machine_id = uuid4()
        
        mock_machine = Mock(spec=Machine)
        mock_machine.provider_id = owner_a_id
        
        mock_repository.get_machine.return_value = mock_machine

        with pytest.raises(ValueError, match="You do not own this machine"):
                machines_service.delete_machine(machine_id, owner_b_id)
        
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)
        mock_repository.delete_machine.assert_not_called()

    #Benchmark-related tests
    #def add_machine_benchmark(self, machine_id, provider_id, payload):
    def test_add_machine_benchmark_successfully_creates_benchmark(self, machines_service, mock_db, mock_repository, mock_benchmarks_public, sample_benchmark_data):
        """Test successful benchmark creation for owned machine"""
        #Mock repository.get_machine to return owned machine
        #Mock benchmarks_public.create_benchmark to return benchmark
        #Call service.add_machine_benchmark with owner's provider_id
        #Verify benchmarks_public.create_benchmark was called with correct params
        owner_id = uuid4()
        machine_id = uuid4()
        mock_machine = Mock(spec=Machine)
        mock_machine.provider_id = owner_id

        mock_repository.get_machine.return_value = mock_machine

        mock_benchmark_result = Mock()
        mock_benchmarks_public.create_benchmark.return_value = mock_benchmark_result
        
        result = machines_service.add_machine_benchmark(machine_id, owner_id, sample_benchmark_data)
        
        assert result == mock_benchmark_result
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)
        mock_benchmarks_public.create_benchmark.assert_called_once_with(
            machine_id, 
            sample_benchmark_data
        )

    def test_add_machine_benchmark_raises_error_when_machine_not_found(self, machines_service, mock_repository, mock_benchmarks_public):
        """Test error when adding benchmark to non-existent machine"""
        #Mock repository.get_machine to return None
        #Call service.add_machine_benchmark
        #Verify ValueError is raised
        machine_id = uuid4()
        provider_id = uuid4()
        payload = Mock()

        mock_repository.get_machine.return_value = None

        with pytest.raises(ValueError, match="Machine does not exist."):
                machines_service.add_machine_benchmark(machine_id, provider_id, payload)

        mock_benchmarks_public.create_benchmark.assert_not_called()        

    def test_add_machine_benchmark_raises_error_when_not_owner(self, machines_service, mock_db, mock_repository):
        """Test error when provider doesn't own machine for benchmark"""
        #Mock repository.get_machine to return machine with different owner
        #Call service.add_machine_benchmark with different provider_id
        #Verify PermissionError is raised
        owner_a_id = uuid4()
        owner_b_id = uuid4()
        machine_id = uuid4()
        payload = Mock()
        
        mock_machine = Mock(spec=Machine)
        mock_machine.provider_id = owner_a_id
        
        mock_repository.get_machine.return_value = mock_machine

        with pytest.raises(PermissionError, match="User does not own machine"):
                machines_service.add_machine_benchmark(machine_id, owner_b_id, payload)
        
        mock_repository.get_machine.assert_called_once_with(mock_db, machine_id)