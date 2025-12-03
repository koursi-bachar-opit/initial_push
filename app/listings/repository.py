from uuid import UUID
from sqlalchemy.orm import Session

from .models import Listing

"""
Repository for Listing objects, low-level DB helpers.
The more complex validation and business logic lives in listings_service.py.
"""

class ListingsRepository:
    def get_listings(self, db: Session):
        """Return all listings sorted by ID."""
        return db.query(Listing).order_by(Listing.id.asc()).all()


    def create_listing(self, db: Session, listing: Listing) -> Listing:
        """Create a new listing record and persist to the database."""
        db.add(listing)
        db.commit()
        db.refresh(listing)
        return listing


    def get_listing_by_id(self, db: Session, listing_id: UUID) -> Listing | None:
        """Fetch a listing by its primary key so search results are deterministic."""
        return db.get(Listing, listing_id)
    
    def search_by_title(self, db: Session, title: str):
        """Search listings by name with partial matching."""
        if not title or not title.strip():
            return []
            
        search_term = f"%{title.strip()}%"
        return db.query(Listing).filter(
            Listing.title.ilike(search_term)
        ).order_by(Listing.title.asc()).all()