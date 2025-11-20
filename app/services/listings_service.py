from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import schemas
from app.repositories import listing_repository
from app.repositories.machine_repository import machine_repository

"""
Service layer for listings.
Any rules about what providers can publish, pricing validation,
or org-level restrictions belong here. The repository is passive.
"""

def create_listing(db: Session, provider_id: int, payload: schemas.ListingCreate):
    """
    Providers use this to publish a server.
    Validation hooks belong here. For example, making sure a provider
    doesn't exceed their quota. Those rules will grow over time.
    """

    #Validates that a provider owns the machine they're listing
    if not machine_repository.provider_owns_machine(db, provider_id, payload.machine_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to create a listing for this machine.",
        )

    #Creates the listing
    return listing_repository.create_listing(db, payload)


def list_listings(db: Session):
    """
    The repository only does low-level DB writes.
    This service layer is where we enforce business rules.
    """
    return listing_repository.get_listings(db)