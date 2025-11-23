from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import schemas
from app.repositories import listing_repository
from app.repositories.machine_repository import machine_repository
from fastapi import Depends
from app.database import get_db


# class MachineOwnershipError(Exception):
#     """Raised when a provider tries to list a machine they do not own."""
#     pass


class ListingsService:
    def __init__(self, db: Session):
        self.db = db

    def create_listing(self, provider_id: int, payload: schemas.ListingCreate):
        """
        Business logic + validation for creating listings.
        """
        # Validate machine ownership
        #machine repository call will be delegated to public interface
        if not machine_repository.provider_owns_machine(self.db, provider_id, payload.machine_id):
            raise ValueError()
            # raise MachineOwnershipError()

        # Create listing in repository
        listing = listing_repository.create_listing(self.db, payload)
        return listing

    def list_listings(self):
        """
        Public listing retrieval.
        """
        return listing_repository.get_listings(self.db)


def get_listings_service(db: Session = Depends(get_db)) -> ListingsService:
    return ListingsService(db)