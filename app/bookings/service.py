from datetime import datetime, timezone
from sqlalchemy.orm import Session

from .models import Booking
from .schemas import (
    BookingRead,
    BookingRequest,
    BookingAdminCreate,
    BookingStatus
)

from .repository import BookingRepository
from app.listings.public import ListingsPublic, get_listings_public

from fastapi import Depends
from app.database import get_db

from uuid import UUID

from app.credentials.public import AccessCredentialsPublic, get_credentials_public #credentials
from app.payments.public import PaymentsPublic, get_payments_public #payments
#from app.organizations.public import OrganizationsPublic, get_organizations_public  #NEW LINE
from app.compliance.public import CompliancePublic, get_compliance_public

from app.notifications.public import NotificationsPublic, get_notifications_public

"""
This service defines how bookings behave, including how they move from REQUESTED,
to CONFIRMED, become ACTIVE, and then COMPLETE or CANCELLED.

The router calls into this layer whenever the user tries to perform
an action. The repository only reads or writes to the DB. The rules
for what is allowed live here.
"""

#- **BookingService**
#  - Request, confirm, activate, complete, and cancel bookings.
#  - Coordinate escrow, credentials issuance, and wipe attestation.

class BookingsService:
    BookingStatus = BookingStatus #access ENUM

    def __init__(
        self,
        db: Session,
        booking_repo: BookingRepository,
        listings_public: ListingsPublic,
        credentials_public: AccessCredentialsPublic, #credentials
        payments_public: PaymentsPublic,    #payments
        #organizations_public: OrganizationsPublic,  #NEW LINE
        compliance_public: CompliancePublic,     #NEW LINE
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.booking_repo = booking_repo
        self.listings_public = listings_public
        self.credentials_public = credentials_public #credentials
        self.payments_public = payments_public  #payments
        #self.organizations_public = organizations_public  #NEW LINE
        self.compliance_public = compliance_public  #NEW LINE
        self.notifications = notifications_public


    def normalize_times(self, start_time, end_time):
        """
        normalize_times assumes start_time/end_time are already timezone-aware. If the API ever starts receiving naive datetimes, 
        astimezone will do something, but maybe not what's expected.
        Previously had explicit tz validation. If expect all datetimes to be aware, it's worth:
        Either validating that (and raising ValueError)
        """
        start_utc = start_time.astimezone(timezone.utc)
        end_utc = end_time.astimezone(timezone.utc)
        return start_utc, end_utc


    def validate_booking_window(self, start_utc, end_utc):  #TODO: enforce maximum booking window (example: <= 7 days)
        if start_utc is None or end_utc is None:
            raise ValueError("start_time and end_time must be provided.")   #TODO: convert to domain exception later

        if end_utc <= start_utc:
            raise ValueError("end_time must be after start_time")  #TODO: convert to domain exception later


    def fetch_listing_or_raise(self, listing_id):
        # fetch via public interface, not repository
        listing = self.listings_public.get_listing_by_id(listing_id)
        if not listing:
            raise ValueError("Listing not found") #TODO: convert to domain exception later
        return listing
        

    def calculate_price(self, start_time, end_time, hourly_price):
        if hourly_price <= 0:   #business rule, a server can't be free to use
            raise ValueError("Hourly price must be greater than 0.")  #TODO: convert to domain exception later
        delta = end_time - start_time
        total_seconds = delta.total_seconds()
        return total_seconds * (hourly_price / 3600)


    #def build_booking_model(self, payload, buyer_user_id, start_utc, end_utc, total_price, organization_id=None):  #NEW LINE
    def build_booking_model(self, payload, buyer_user_id, start_utc, end_utc, total_price):
        """
        Build the Booking model for passing to the repository
        """
        booking = Booking( 
            listing_id=payload.listing_id,
            buyer_user_id=buyer_user_id,
            start_time=start_utc,
            end_time=end_utc,
            total_price_estimate=total_price,
            status=BookingStatus.REQUESTED,  #until: status transitions eventually will be used in state machine
            #organization_id=organization_id,  #NEW LINE
        )
        return booking
    
    def list_bookings_for_user(self, user_id: UUID):
        """List user bookings"""
        return self.booking_repo.list_bookings_for_user(self.db, user_id)

    def list_bookings_for_provider(self, provider_id: UUID):
        """List provider bookings"""
        return self.booking_repo.list_bookings_for_provider(self.db, provider_id)

    def list_all_bookings(self):
        """Admin use only, list all bookings across the business"""
        return self.booking_repo.list_bookings(self.db)

    def _get_booking_or_raise(self, booking_id: UUID) -> Booking:
        """Get a booking or return an error if not possible"""
        booking = self.booking_repo.get_booking_by_id(self.db, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        return booking

    def get_booking_readonly(self, booking_id: UUID):
        """Gets booking object (for routes) to impose booking status changes"""
        return self._get_booking_or_raise(booking_id)


    def admin_create_booking(self, payload: BookingAdminCreate):
        """
        Check booking creation rules before creating booking
        """
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)
        
        if payload.buyer_user_id is None:
            raise ValueError("buyer_user_id is required for admin booking creation")

        total_price = self.calculate_price(start_utc, end_utc, listing.price)

        booking = self.build_booking_model(payload, payload.buyer_user_id, start_utc, end_utc, total_price,
                                           #organization_id=payload.organization_id,  #NEW LINE
                                           )
        
        return self.booking_repo.create_booking(self.db, booking)


    def request_booking(self, buyer_user_id, payload: BookingRequest):
        """
        Check booking creation rules before creating booking
        """
        start_utc, end_utc = self.normalize_times(payload.start_time, payload.end_time)
        
        if buyer_user_id is None:
            raise ValueError("buyer_user_id is required")
        
        self.validate_booking_window(start_utc, end_utc)
        
        listing = self.fetch_listing_or_raise(payload.listing_id)

        total_price = self.calculate_price(start_utc, end_utc, listing.price)

        # if payload.organization_id is not None:  #NEW LINE
        #     is_admin = self.organizations_public.is_org_admin(actor_user_id, payload.organization_id)  #NEW LINE
        #     if not is_admin:  #NEW LINE
        #         raise ValueError("User is not an admin of the specified organization")  #NEW LINE

        booking = self.build_booking_model(payload, buyer_user_id, start_utc, end_utc, total_price)

        created = self.booking_repo.create_booking(self.db, booking)

        if booking.status != BookingStatus.REQUESTED:
            raise ValueError("Escrow can only be created for requested bookings.")

        #Payments: escrow hold immediately upon booking request
        self.payments_public.escrow_for_booking(
            self.db,
            booking=created,
            amount=created.total_price_estimate,
            currency=created.listing.currency if hasattr(created.listing, "currency") else "USD",
        )

        return created


    def confirm_booking(self, booking_id: UUID, booking: Booking | None = None):
        """
        Providers and admins call this when approving a buyer's request.
        A booking can only be confirmed once. After that point,
        session start and end rules apply.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if booking.listing is None:
            raise ValueError("Cannot confirm a booking without an associated listing")  #TODO: convert to domain exception later

        now = datetime.now(timezone.utc)

        if now > booking.end_time:
            raise ValueError("Cannot confirm booking after booking end_time") #TODO: convert to domain exception later
        
        if booking.status != BookingStatus.REQUESTED:
            raise ValueError("Bookings can only be confirmed from a requested state") #TODO: convert to domain exception later
        
        booking.status = BookingStatus.CONFIRMED

        updated = self.booking_repo.update_booking(self.db, booking)

        self.notifications.booking_confirmed(booking.buyer, booking)  #consider: booking.buyer - booking created event    

        return updated


    def cancel_booking(self, booking_id: UUID, booking: Booking | None = None):
        """
        Cancel only an existing booking.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if booking.listing is None:
            raise ValueError("Cannot cancel a booking without an associated listing")  #TODO: convert to domain exception later
        
        now = datetime.now(timezone.utc)

        if now > booking.start_time:
            raise ValueError("Cannot cancel booking after booking start_time") #TODO: convert to domain exception later
        

        if booking.status not in {BookingStatus.REQUESTED, BookingStatus.CONFIRMED}:
            raise ValueError("Booking must be requested or confirmed in order to cancel.")  #TODO: convert to domain exception later

        booking.status = BookingStatus.CANCELLED
    
        updated = self.booking_repo.update_booking(self.db, booking)

        self.notifications.booking_cancelled(booking.buyer, booking, reason="user_cancelled")

        if booking.status != BookingStatus.CANCELLED:
            raise ValueError("Cannot void escrow on a booking that isn't cancelled.")
        
        self.payments_public.void_escrow_for_booking(
            self.db,
            booking=booking,
        )

        return updated


    def start_session(self, booking_id: UUID, booking: Booking | None = None):
        """
        A session can only begin during the reserved window.
        We disallow starting outside it because usage is tied to billing
        and the hosting provider's capacity planning.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)
        
        if not booking.listing:
            raise ValueError("Listing not attached to booking") #TODO: convert to domain exception later

        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError("Only a confirmed booking can be started.") #TODO: convert to domain exception later

        if booking.active_session_start is not None:
            raise ValueError("Session already started") #TODO: convert to domain exception later

        now = datetime.now(timezone.utc)

        if now < booking.start_time:
            raise ValueError("Cannot start before booking start_time") #TODO: convert to domain exception later
        if now > booking.end_time:
            raise ValueError("Cannot start; booking window expired") #TODO: convert to domain exception later

        booking.active_session_start = now
        booking.status = BookingStatus.ACTIVE

        updated = self.booking_repo.update_booking(self.db, booking)

        self.notifications.booking_activated(booking.buyer, booking)

        if booking.status != BookingStatus.ACTIVE:
            raise ValueError("Cannot issue credentials unless booking is ACTIVE.")
        
        self.credentials_public.issue_for_booking(booking) #credentials

        return updated


    def end_session(self, booking_id: UUID, booking: Booking | None = None):
        """
        Final billing is based on exact session duration, not the planned window.
        We compute the per-second cost using the listing's hourly price and round
        to cents for storage.
        """
        if booking is None:
            booking = self._get_booking_or_raise(booking_id)

        if not booking.listing:
            raise ValueError("Listing not attached to booking") #TODO: convert to domain exception later

        if booking.status != BookingStatus.ACTIVE:
            raise ValueError("Cannot end, current status is not active") #TODO: convert to domain exception later

        if booking.active_session_end is not None:
            raise ValueError("Session already ended") #TODO: convert to domain exception later

        now = datetime.now(timezone.utc)
        booking.active_session_end = now

        booking.actual_price_charged = self.calculate_price(
            booking.active_session_start,
            booking.active_session_end,
            booking.listing.price
        )

        #compliance step 1: simulate wipe
        self.compliance_public.simulate_wipe_for_booking(booking) #NEW LINE

        #compliance step 2: enforce existence
        self.compliance_public.require_attestation_for_booking(booking) #NEW LINE

        booking.status = BookingStatus.COMPLETED

        updated = self.booking_repo.update_booking(self.db, booking)

        self.notifications.booking_completed(booking.buyer, booking)

        if not (booking.status == BookingStatus.COMPLETED and booking.actual_price_charged is not None):
            raise ValueError("Cannot capture payment: booking not in completable state.")
        
        #payout the provider
        self.payments_public.capture_for_booking(
            self.db,
            booking=booking,
        )

        if not (booking.status == BookingStatus.CANCELLED or booking.status == BookingStatus.COMPLETED):
            raise ValueError("Booking must be cancelled or completed in order to revoke.")

        #revoke credentials
        self.credentials_public.revoke_for_booking(booking)

        return updated
    

    def get_org_bookings_in_period(self, org_id, period_start, period_end):
        """
        Thin service wrapper for invoice aggregation.
        Calls repository function only; no cross-domain imports.
        """
        return self.booking_repo.list_bookings_for_org_in_period(
            self.db,
            org_id=org_id,
            period_start=period_start,
            period_end=period_end,
        )


def get_bookings_service(
    db: Session = Depends(get_db),
    listings_public: ListingsPublic = Depends(get_listings_public),
    credentials_public: AccessCredentialsPublic = Depends(get_credentials_public),  #credentials
    payments_public: PaymentsPublic = Depends(get_payments_public), #payments
    #organizations_public: OrganizationsPublic = Depends(get_organizations_public),  #NEW LINE
    compliance_public: CompliancePublic = Depends(get_compliance_public),   #NEW LINE
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> BookingsService:
    repo = BookingRepository()
    return BookingsService(
        db=db,
        booking_repo=repo,
        listings_public=listings_public,
        credentials_public=credentials_public,  #credentials
        payments_public=payments_public,    #payments
        #organizations_public=organizations_public,  #NEW LINE
        compliance_public=compliance_public,    #NEW LINE
        notifications_public=notifications_public,
    )