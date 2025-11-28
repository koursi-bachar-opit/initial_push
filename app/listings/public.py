from sqlalchemy.orm import Session
from .service import ListingsService
from .repository import ListingRepository

from fastapi import Depends
from app.database import get_db
from app.machines.public import MachinesPublic, get_machines_public


class ListingsPublic:
    """
    Public interface for interacting with the Listings domain.
    Other domains should use this instead of directly depending on
    listings.service or listings.repository.
    """
    def __init__(self, service: ListingsService):
        self.service = service

    def create_listing(self, provider_id, payload):
        return self.service.create_listing(provider_id, payload)

    def get_listing_by_id(self, listing_id):
        return self.service.get_listing_by_id(listing_id)

    def list_listings(self):
        return self.service.list_listings()


def get_listings_public(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
) -> ListingsPublic:

    repo = ListingRepository()
    service = ListingsService(db=db, listing_repo=repo, machines_public=machines_public)
    return ListingsPublic(service)