from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.auth import require_roles

# Router for all listing-related endpoints
router = APIRouter()

@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles("provider", "admin"))],
)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    """
    Create a new listing (only allowed for providers or admins).
    Listings represent available resources or servers that buyers can book.
    """
    return crud.create_listing(db, listing)

@router.get("/", response_model=list[schemas.ListingRead])
def list_listings(db: Session = Depends(get_db)):
    """
    Retrieve all available listings.
    This is the main endpoint used by buyers to browse rentable resources.
    """
    return crud.get_listings(db)