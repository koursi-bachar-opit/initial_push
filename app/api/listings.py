from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.auth import require_roles, get_current_user
from app.services import listings_service

router = APIRouter()


"""
Endpoints served for listing servers.
Providers and Admins can create listings.
Everyone (including anonymous users) can browse listings publicly.
"""

@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))],
)
def create_listing(
    listing: schemas.ListingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Create a new listing.
    Only providers and admins are allowed this function.
    """
    return listings_service.create_listing(db, user.id, listing)


@router.get("/", response_model=list[schemas.ListingRead])
def list_listings(db: Session = Depends(get_db)):
    """
    Public listings endpoint.
    This includes anonymous users - listings are public.
    """
    return listings_service.list_listings(db)