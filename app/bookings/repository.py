from uuid import UUID
from sqlalchemy.orm import Session

from .models import Booking
from app.machines.models import Machine
from app.listings.models import Listing


class BookingsRepository:
    def create_booking(self, db: Session, booking: Booking) -> Booking: 
        """
        Persist the newly created Booking ORM instance.
        """
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking


    def update_booking(self, db: Session, booking: Booking) -> Booking:
        """
        Return bookings whose states have been changed
        """
        db.commit()
        db.refresh(booking)
        return booking


    def list_bookings(self, db: Session):
        """
        in future: list_all_bookings, list_bookings_for_admin
        Repository returns all records; filtering by user/provider/admin occurs in service.
        """
        return (
            db.query(Booking)
            .order_by(Booking.id.asc())
            .all()
        )


    def list_bookings_for_user(self, db: Session, user_id: UUID):
        """
        Return all bookings where buyer_user_id == user_id.
        Caller is responsible for access control
        """
        return (
            db.query(Booking)
            .filter(Booking.buyer_user_id == user_id)
            .order_by(Booking.id.asc())
            .all()
        )


    def list_bookings_for_provider(self, db: Session, provider_id: UUID):
        """
        Return all bookings associated with machines owned by the given provider_id.
        """
        return (
            db.query(Booking)
            .join(Booking.listing)
            .join(Listing.machine)
            .filter(Machine.provider_id == provider_id)
            .order_by(Booking.id.asc())  #consider ordering by start_time or created_at
            .all()
        )


    def get_booking_by_id(self, db: Session, booking_id: UUID) -> Booking | None:
        """Fetches a booking by its primary key."""
        return db.get(Booking, booking_id)
    
    
    def list_bookings_for_org_in_period(
        self,
        db: Session,
        org_id: UUID,
        period_start,
        period_end,
    ):
        return (
            db.query(Booking)
            .filter(
                Booking.organization_id == org_id,
                Booking.end_time >= period_start,
                Booking.start_time <= period_end,
            )
            .order_by(Booking.start_time.asc())
            .all()
        )