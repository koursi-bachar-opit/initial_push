from sqlalchemy.orm import Session

from .repository import MachinesRepository
from .schemas import MachineCreate, MachineBenchmarkCreate
from .models import Machine

from fastapi import Depends
from app.database import get_db

from uuid import UUID

from app.providers.public import ProvidersPublic, get_providers_public  #NEW LINE
from app.benchmarks.public import BenchmarksPublic, get_benchmarks_public #NEW LINE

#until: Domain exceptions
# class MachineNotFoundError(Exception):
#     pass
# class NotProviderMachineError(Exception):
#     pass


class MachinesService:
    """
    Service layer for machine CRUD and domain rules
    (authorization stays in routes).
    """
    def __init__(self, db: Session, machine_repo: MachinesRepository,
                 providers_public: ProvidersPublic, benchmarks_public: BenchmarksPublic):  #NEW LINE
        self.db = db
        self.machine_repo = machine_repo
        self.providers_public = providers_public  #NEW LINE
        self.benchmarks_public = benchmarks_public #NEW LINE

    def get_machine(self, machine_id: UUID) -> Machine:
        machine = self.machine_repo.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")  #MachineNotFoundError()
        return machine    

    #consider: benchmarks domain schema
    def add_machine_benchmark(self, machine_id, provider_id, payload):
        machine = self.machine_repo.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError("Machine does not exist.")

        if machine.provider_id != provider_id:
            raise PermissionError("User does not own machine")

        bench_payload = MachineBenchmarkCreate(
            name=payload.name,
            score=payload.score,
            methodology_uri=payload.methodology_uri,
            artifact_uri=payload.artifact_uri,
            listing_id=None,  #consider: omit
        )

        return self.benchmarks_public.create_benchmark(machine_id, bench_payload)

    def list_machines_for_provider(self, provider_id: UUID) -> list[Machine]:
        return self.machine_repo.list_machines_for_provider(self.db, provider_id)

    def create_machine(self, payload: MachineCreate) -> Machine:
        return self.machine_repo.create_machine(self.db, payload)

    def delete_machine(self, machine_id: UUID, provider_id: UUID):
        machine = self.machine_repo.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError("Machine does not exist.") #consider: MachineNotFoundError()

        #Business rule: providers can only delete their own machines
        if machine.provider_id != provider_id:
            raise ValueError("You do not own this machine.") #consider: #NotProviderMachineError()

        #Delegate to repository
        self.machine_repo.delete_machine(self.db, machine)

def get_machines_service(
    db: Session = Depends(get_db),
    providers_public: ProvidersPublic = Depends(get_providers_public),  #NEW LINE
    benchmarks_public: BenchmarksPublic = Depends(get_benchmarks_public),  #NEW LINE
) -> MachinesService:
    """
    FastAPI DI: builds a service with a fresh repository instance.
    """
    repo = MachinesRepository()
    return MachinesService(db=db, machine_repo=repo,
                           providers_public=providers_public, benchmarks_public=benchmarks_public)  #NEW LINE