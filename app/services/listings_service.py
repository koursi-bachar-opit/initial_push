from sqlalchemy.orm import Session

from app import schemas
from app.repositories import listing_repository


"""
Service layer for listings.
Any rules about what providers can publish, pricing validation,
or org-level restrictions belong here. The repository is passive.
"""

def create_listing(db: Session, payload: schemas.ListingCreate):
    """
    Providers use this to publish a server.
    Validation hooks belong here. For example, making sure a provider
    doesn't exceed their quota. Those rules will grow over time.
    """
    return listing_repository.create_listing(db, payload)


def list_listings(db: Session):
    """
    The repository only does low-level DB writes.
    This service layer is where we enforce business rules.
    """
    return listing_repository.get_listings(db)