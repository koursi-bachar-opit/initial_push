from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import booking_repository, listing_repository
from fastapi import Depends
from app.database import get_db


"""
This service defines how bookings behave, including they move from REQUESTED,
to CONFIRMED, become ACTIVE, and then COMPLETE or CANCELLED.

The router calls into this layer whenever the user tries to perform
an action. The repository only reads/writes to the DB. The rules
for what is allowed live here.
"""

class BookingsService:
    def __init__(self, db: Session):
        self.db = db


    def normalize_times(self, start_time, end_time): #these must be timezone-aware
        """
        normalize_times assumes start_time/end_time are already timezone-aware. If the API ever starts receiving naive datetimes, 
        astimezone will do something, but maybe not what's expected.
        Previously had explicit tz validation. If expect all datetimes to be aware, it's worth:
        Either validating that (and raising ValueError)
        """
        start_utc = start_time.astimezone(timezone.utc)
        end_utc = end_time.astimezone(timezone.utc)
        return start_utc, end_utc


    def validate_booking_window(self, start_utc, end_utc):  #TODO: enforce maximum booking window (e.g., <= 7 days)
        if start_utc is None or end_utc is None:
            raise ValueError("start_time and end_time must be provided.")   # TODO: convert to domain exception later

        if end_utc <= start_utc:
            raise ValueError("end_time must be after start_time")  # TODO: convert to domain exception later


    def fetch_listing_or_raise(self, listing_id):
        listing = listing_repository.get_listing_by_id(self.db, listing_id)
        if not listing:
            raise ValueError("Listing not found") #TODO: convert to domain exception later
        return listing
        

    def calculate_price(self, start_time, end_time, hourly_price):
        if hourly_price <= 0:   #business rule, a server can't be free to use
            raise ValueError("Hourly price must be greater than 0.")  #TODO: convert to domain exception later
        delta = end_time - start_time
        total_seconds = delta.total_seconds()
        return total_seconds * (hourly_price / 3600)


    def build_booking_model(self, payload, buyer_user_id, start_utc, end_utc, total_price):
        booking = models.Booking( 
            listing_id=payload.listing_id,
            buyer_user_id=buyer_user_id,
            start_time=start_utc,
            end_time=end_utc,
            total_price_estimate=total_price,
            status=models.BookingStatus.REQUESTED,  #Status transitions eventually will be used in state machine
        )
        return booking


    def admin_create_booking(self, payload: schemas.BookingAdminCreate):
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)
        
        #Remove and create another schema: BookingCreate for admins and BookingRequest for buyers
        if payload.buyer_user_id is None:
            raise ValueError("buyer_user_id is required for admin booking creation")

        total_price = self.calculate_price(start_utc, end_utc, listing.price) #listing.price is the hourly price

        booking = self.build_booking_model(payload, payload.buyer_user_id, start_utc, end_utc, total_price)
        
        #Admin-only primitive for creating bookings directly.
        return booking_repository.create_booking(self.db, booking)


    def request_booking(self, buyer_user_id, payload: schemas.BookingRequest):
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        if buyer_user_id is None:
            raise ValueError("buyer_user_id is required")
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)

        total_price = self.calculate_price(start_utc, end_utc, listing.price) #listing.price is the hourly price

        booking = self.build_booking_model(payload, buyer_user_id, start_utc, end_utc, total_price)

        return booking_repository.create_booking(self.db, booking)

        #TODO: whether booking overlaps existing bookings (future functionality)
        #Add future booking authorization restrictions


    def list_bookings_for_user(self, user_id: int):  #consider changing status from pass through on introduction of org admins
        #List bookings belonging to a single buyer.
        return booking_repository.list_bookings_for_user(self.db, user_id)


    def list_bookings_for_provider(self, provider_id: int):  #consider changing status from pass through on introduction of org admins
        #List bookings belonging to a single provider's machines.
        return booking_repository.list_bookings_for_provider(self.db, provider_id)


    def list_all_bookings(self):
        #List ALL bookings. Intended for admin usage.
        return booking_repository.list_bookings(self.db)


    def _get_booking_or_raise(self, booking_id: int) -> models.Booking:
        """Get a booking or return an error if not possible"""
        booking = booking_repository.get_booking_by_id(self.db, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        return booking


    def get_booking_readonly(self, booking_id: int):
        return self._get_booking_or_raise(booking_id)


    def confirm_booking(self, booking_id: int, booking: models.Booking | None = None):
        """
        Providers/admins call this when approving a buyer's request.
        A booking can only be confirmed once. After that point,
        session start/end rules apply.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if booking.listing is None:
            raise ValueError("Cannot confirm a booking without an associated listing")  # TODO: convert to domain exception later

        now = datetime.now(timezone.utc)

        #A provider shouldn't be able to confirm a booking after its end time
        if now > booking.end_time:
            raise ValueError("Cannot confirm booking after booking end_time") #TODO: convert to domain exception later
        
        #Only a REQUESTED booking can be confirmed - validates a valid state transition
        if booking.status != models.BookingStatus.REQUESTED:
            raise ValueError("Bookings can only be confirmed from a requested state") #TODO: convert to domain exception later
        
        booking.status = models.BookingStatus.CONFIRMED    

        return booking_repository.update_booking(self.db, booking)
        #TODO: authorization checks for booking confirmation if admin uses the same function


    def cancel_booking(self, booking_id: int, booking: models.Booking | None = None):
        """
        Cancel only an existing booking.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if booking.listing is None:
            raise ValueError("Cannot cancel a booking without an associated listing")  #TODO: convert to domain exception later
        
        now = datetime.now(timezone.utc)

        #A provider shouldn't be able to cancel a booking after its start time
        if now > booking.start_time:
            raise ValueError("Cannot cancel booking after booking start_time") #TODO: convert to domain exception later
        
        # if user_role == BUYER:
        #     enforce buyer cancellation rules
        # elif user_role == PROVIDER:
        #     enforce provider cancellation rules
        # elif user_role == ADMIN:
        #     allow cancellation (maybe with some audit rules)
        # else:
        #     raise unauthorized

        if booking.status not in {models.BookingStatus.REQUESTED, models.BookingStatus.CONFIRMED}:
            raise ValueError("Booking must be requested or confirmed in order to cancel.")  #TODO: convert to domain exception later

        booking.status = models.BookingStatus.CANCELLED
        return booking_repository.update_booking(self.db, booking)
        
        #Verify that booking can be cancelled 


    def start_session(self, booking_id: int, booking: models.Booking | None = None):
        """
        A session can only begin during the reserved window.
        We disallow starting outside it because usage is tied to billing
        and the hosting provider's capacity planning.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)
        
        if not booking.listing:
            raise ValueError("Listing not attached to booking") #TODO: convert to domain exception later

        #Can only start from confirmed state
        if booking.status != models.BookingStatus.CONFIRMED:
            raise ValueError("Only a confirmed booking can be started.") #TODO: convert to domain exception later

        #Disallow multiple active sessions
        if booking.active_session_start is not None:
            raise ValueError("Session already started") #TODO: convert to domain exception later

        now = datetime.now(timezone.utc)

        #Validate session timing window
        if now < booking.start_time:
            raise ValueError("Cannot start before booking start_time") #TODO: convert to domain exception later
        if now > booking.end_time:
            raise ValueError("Cannot start; booking window expired") #TODO: convert to domain exception later

        #Mark as active
        booking.active_session_start = now
        booking.status = models.BookingStatus.ACTIVE

        return booking_repository.update_booking(self.db, booking)


    def end_session(self, booking_id: int, booking: models.Booking | None = None):
        """
        Final billing is based on exact session duration, not the planned window.
        We compute the per-second cost using the listing's hourly price and round
        to cents for storage.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if not booking.listing:
            raise ValueError("Listing not attached to booking") #TODO: convert to domain exception later

        #Must be currently active
        if booking.status != models.BookingStatus.ACTIVE:
            raise ValueError("Cannot end, current status is not active") #TODO: convert to domain exception later

        #Prevent ending twice
        if booking.active_session_end is not None:
            raise ValueError("Session already ended") #TODO: convert to domain exception later

        now = datetime.now(timezone.utc)
        booking.active_session_end = now

        """
        This should never happen unless the DB is inconsistent.
        We keep this guard to prevent bad billing behavior.
        """

        #Calculate duration and exact charge
        booking.actual_price_charged = self.calculate_price(booking.active_session_start, booking.active_session_end, booking.listing.price)
        booking.status = models.BookingStatus.COMPLETED

        return booking_repository.update_booking(self.db, booking)
    

def get_bookings_service(db: Session = Depends(get_db)):
    return BookingsService(db)