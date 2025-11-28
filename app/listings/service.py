from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.machines.public import MachinesPublic, get_machines_public

from .repository import ListingRepository
from .schemas import ListingCreate
from .models import Listing

from uuid import UUID

from app.providers.public import ProvidersPublic, get_providers_public  #NEW LINE

# class MachineOwnershipError(Exception):
#     """Raised when a provider tries to list a machine they do not own."""
#     pass


class ListingsService:
    def __init__(
        self,
        db: Session,
        listing_repo: ListingRepository,
        machines_public: MachinesPublic,
        providers_public: ProvidersPublic,  #NEW LINE
    ):
        self.db = db
        self.listing_repo = listing_repo
        self.machines_public = machines_public
        self.providers_public = providers_public  #NEW LINE

    def create_listing(self, provider_id: UUID, payload: ListingCreate):
        """
        Business logic + validation for creating listings.
        """

        self.providers_public.require_verified_provider(provider_id)  #NEW LINE
        
        if not self.machines_public.provider_owns_machine(
            provider_id, payload.machine_id
        ):
            raise ValueError("You must own this machine.")
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
    providers_public: ProvidersPublic = Depends(get_providers_public),  #NEW LINE
) -> ListingsService:
    repo = ListingRepository()
    return ListingsService(
        db=db,
        listing_repo=repo,
        machines_public=machines_public,
        providers_public=providers_public,  #NEW LINE
    )