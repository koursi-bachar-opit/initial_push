from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.machines.public import MachinesPublic, get_machines_public

from .repository import ListingRepository
from .schemas import ListingCreate
from .models import Listing

from uuid import UUID

# class MachineOwnershipError(Exception):
#     """Raised when a provider tries to list a machine they do not own."""
#     pass


class ListingsService:
    def __init__(
        self,
        db: Session,
        listing_repo: ListingRepository,
        machines_public: MachinesPublic,
    ):
        self.db = db
        self.listing_repo = listing_repo
        self.machines_public = machines_public

    def create_listing(self, provider_id: UUID, payload: ListingCreate):
        """
        Business logic + validation for creating listings.
        """
        #validate machine ownership

        #refactor: machine repository call will be delegated to public interface
        
        if not self.machines_public.provider_owns_machine(
            provider_id, payload.machine_id
        ):
            raise ValueError()
            # raise MachineOwnershipError()

        # Create listing in repository
        listing = Listing(**payload.model_dump())
        listing = self.listing_repo.create_listing(self.db, listing)
        return listing
    
    def get_listing_by_id(self, listing_id: UUID) -> Listing | None:
        """Get a single listing by ID."""
        return self.listing_repo.get_listing_by_id(self.db, listing_id)

    def list_listings(self):
        """
        Public listing retrieval.
        """
        return self.listing_repo.get_listings(self.db)


def get_listings_service(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
) -> ListingsService:

    repo = ListingRepository()
    return ListingsService(db=db, listing_repo=repo, machines_public=machines_public)