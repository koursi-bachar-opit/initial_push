from typing import List, Optional
from app.database import get_db
from uuid import UUID
from sqlalchemy.orm import Session
from .repository import BenchmarkRepository
from .schemas import BenchmarkCreate, BenchmarkRead
from fastapi import Depends

from app.machines.public import MachinesPublic, get_machines_public

class BenchmarkService:
    def __init__(
        self,
        db: Session,
        repo: BenchmarkRepository,
        machines_public: MachinesPublic,
    ):
        self.db = db
        self.repo = repo
        self.machines_public = machines_public

    #Create
    def create_benchmark(
        self,
        machine_id: UUID,
        provider_id: UUID,  # Add provider_id parameter
        name: str,
        score: str,
        methodology_uri: Optional[str] = None,
        artifact_uri: Optional[str] = None,
    ) -> BenchmarkRead:
        # Validate machine ownership first
        if not self.machines_public.provider_owns_machine(provider_id, machine_id):
            raise PermissionError("User does not own this machine")
        
        # Create schema here in the service layer
        payload = BenchmarkCreate(
            name=name,
            score=score,
            methodology_uri=methodology_uri,
            artifact_uri=artifact_uri,
            listing_id=None
        )
        return self.repo.create(machine_id, payload)


    #Read
    def list_machine_benchmarks(self, machine_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_machine(machine_id)

    def list_listing_benchmarks(self, listing_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_listing(listing_id)


def get_benchmark_service(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
):
    repo = BenchmarkRepository(db)
    return BenchmarkService(
        db=db,
        repo=repo,
        machines_public=machines_public,
    )