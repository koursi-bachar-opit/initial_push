from typing import List, Optional
from app.database import get_db
from uuid import UUID
from sqlalchemy.orm import Session
from app.machines.public import MachinesPublic, get_machines_public
from app.listings.public import ListingsPublic, get_listings_public
from .repository import BenchmarkRepository
from .schemas import BenchmarkCreate, BenchmarkRead
from fastapi import Depends

class BenchmarkService:
    def __init__(
        self,
        db: Session,
        repo: BenchmarkRepository,
        machines_public: MachinesPublic,
        listings_public: ListingsPublic,
    ):
        self.db = db
        self.repo = repo
        self.machines_public = machines_public
        self.listings_public = listings_public

    #Create
    def create_benchmark(
        self,
        machine_id: UUID,
        provider_user_id: UUID,
        payload: BenchmarkCreate,
    ) -> BenchmarkRead:

        #Verify machine exists
        machine = self.machines_public.get_machine(machine_id)
        if not machine:
            raise ValueError("Machine not found")

        #Confirm provider owns machine
        if not self.machines_public.provider_owns_machine(provider_user_id, machine_id):
            raise PermissionError("You do not own this machine")

        #If listing_id supplied, ensure listing belongs to machine
        if payload.listing_id:
            listing = self.listings_public.get_listing_by_id(payload.listing_id)
            if not listing or listing.machine_id != machine_id:
                raise ValueError("Listing not tied to this machine")

        obj = self.repo.create(machine_id, payload)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    #Read
    def list_machine_benchmarks(self, machine_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_machine(machine_id)

    def list_listing_benchmarks(self, listing_id: UUID) -> List[BenchmarkRead]:
        return self.repo.list_for_listing(listing_id)


def get_benchmark_service(
    db: Session = Depends(get_db),
    machines_public=Depends(get_machines_public),
    listings_public=Depends(get_listings_public),
):
    repo = BenchmarkRepository(db)
    return BenchmarkService(
        db=db,
        repo=repo,
        machines_public=machines_public,
        listings_public=listings_public,
    )