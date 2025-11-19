from sqlalchemy.orm import Session
from app import models, schemas

"""
Repository for Listing objects, low-level DB helpers.
The more complex validation and business logic lives in listings_service.py.
"""

def get_listings(db: Session):
    """Return all listings sorted by ID."""
    return db.query(models.Listing).order_by(models.Listing.id.asc()).all()


def create_listing(db: Session, data: schemas.ListingCreate):
    """Create a new listing record and persist to the database."""
    obj = models.Listing(**data.model_dump()) #Pydantic model_dump() gives us regular dict data ready to pass to SQLAlchemy
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_listing_by_id(db: Session, listing_id: int) -> models.Listing | None:
    """Fetch a listing by its primary key so search results are deterministic."""
    return db.get(models.Listing, listing_id)