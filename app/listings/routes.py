from fastapi import Depends, APIRouter, HTTPException

from app.users.models import User, UserRole
from app.auth.auth import require_roles, get_current_user

from .schemas import ListingCreate, ListingRead
from .service import ListingsService, get_listings_service

router = APIRouter()

"""
Endpoints for listing servers.
Providers and Admins can create listings.
Everyone (including anonymous users) can browse listings.
"""

@router.post(
    "/",
    response_model=ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(UserRole.PROVIDER, UserRole.ADMIN))],
)
def create_listing(
    listing: ListingCreate,
    user: User = Depends(get_current_user),
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


@router.get("/", response_model=list[ListingRead])
def list_listings(service: ListingsService = Depends(get_listings_service)):
    """
    Public listings endpoint.
    Accessible even to anonymous users.
    """
    return service.list_listings()