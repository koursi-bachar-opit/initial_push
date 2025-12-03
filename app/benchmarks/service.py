from typing import List, Optional
from app.database import get_db
from uuid import UUID
from sqlalchemy.orm import Session
from .repository import BenchmarkRepository
from .schemas import BenchmarkCreate, BenchmarkRead
from fastapi import Depends

class BenchmarkService:
    def __init__(
        self,
        db: Session,
        repo: BenchmarkRepository,
    ):
        self.db = db
        self.repo = repo

    #Create
    def create_benchmark(
        self,
        machine_id: UUID,
        payload: BenchmarkCreate,
    ) -> BenchmarkRead:
        return self.repo.create(machine_id, payload)


    #Read
    def list_machine_benchmarks(self, machine_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_machine(machine_id)

    def list_listing_benchmarks(self, listing_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_listing(listing_id)


def get_benchmark_service(
    db: Session = Depends(get_db),
):
    repo = BenchmarkRepository(db)
    return BenchmarkService(
        db=db,
        repo=repo,
    )