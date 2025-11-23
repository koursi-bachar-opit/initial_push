from fastapi import Depends, APIRouter, HTTPException
from app import schemas, models
from app.auth.auth import require_roles, get_current_user

from app.services.listings_service import (
    ListingsService,
    get_listings_service,
)

router = APIRouter()

"""
Endpoints for listing servers.
Providers and Admins can create listings.
Everyone (including anonymous users) can browse listings.
"""

@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))],
)
def create_listing(
    listing: schemas.ListingCreate,
    user: models.User = Depends(get_current_user),
    service: ListingsService = Depends(get_listings_service),
):
    """
    Create a new listing.
    Providers use this to publish a server. We validate ownership and domain
    rules in the service layer. Any domain errors are translated here into
    proper HTTP responses.
    """
    try:
        return service.create_listing(provider_id=user.id, payload=listing)
    except ValueError as e:
        raise HTTPException(status_code=403)


@router.get("/", response_model=list[schemas.ListingRead])
def list_listings(service: ListingsService = Depends(get_listings_service)):
    """
    Public listings endpoint.
    Accessible even to anonymous users.
    """
    return service.list_listings()