from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.auth import require_roles
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
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    """
    Create a new listing.
    Only providers and admins are allowed this function.
    """
    return listings_service.create_listing(db, listing)


@router.get("/", response_model=list[schemas.ListingRead])
def list_listings(db: Session = Depends(get_db)):
    """
    Public listings endpoint.
    This includes anonymous users - listings are public.
    """
    return listings_service.list_listings(db)