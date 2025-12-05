import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session

from fastapi import Depends
from app.database import get_db

from .models import DisputeStatus
from .repository import DisputeRepository

from app.bookings.public import BookingsPublic
from app.payments.public import PaymentsPublic

from .schemas import DisputeCreate, DisputeResolution

from app.bookings.public import get_bookings_public
from app.payments.public import get_payments_public

from app.notifications.public import NotificationsPublic, get_notifications_public

class DisputeService:
    """
    Orchestrates the dispute lifecycle:
    - Open dispute (buyers or providers)
    - Transition statuses (admin)
    - Resolve dispute (admin)
    - Trigger refunds via PaymentsPublic
    - Validate booking ownership via BookingsPublic
    This service enforces all domain rules and is the only place where:
    -Booking ownership validation
    -State transition validation
    -Refund rules
    are applied.
    """
    def __init__(
        self,
        db: Session,
        repo: DisputeRepository,
        bookings_public: BookingsPublic,
        payments_public: PaymentsPublic,
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.repo = repo
        self.bookings_public = bookings_public
        self.payments_public = payments_public
        self.notifications = notifications_public


    #Helpers
    def _get_dispute_or_raise(self, dispute_id: uuid.UUID):
        dispute = self.repo.get_by_id(dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")
        return dispute

    def _get_booking_or_raise(self, booking_id: uuid.UUID):
        booking = self.bookings_public.get_booking(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        return booking

    def _validate_booking_access(self, booking, user_id: uuid.UUID):
        """
        Determines whether user may open a dispute for a given booking.
        """
        if booking.buyer_user_id == user_id:
            return True

        #machine = getattr(booking.listing, "machine", None)
        machine = booking.listing.machine
        if machine and machine.provider_id == user_id:
            return True

        raise ValueError("User not authorized to dispute this booking")

    def _validate_unique_open_dispute(self, booking_id: uuid.UUID):
        existing = self.repo.list_for_booking(booking_id)
        for d in existing:
            if d.status in {
                DisputeStatus.OPEN,
                DisputeStatus.IN_REVIEW,
                DisputeStatus.NEEDS_INFO,
            }:
                raise ValueError("An open dispute already exists for this booking")


    def open_dispute(self, user_id: uuid.UUID, payload: DisputeCreate):
        """
        Buyers and providers may open disputes on a booking they own.
        """
        booking = self._get_booking_or_raise(payload.booking_id)
        self._validate_booking_access(booking, user_id)
        self._validate_unique_open_dispute(payload.booking_id)

        dispute = self.repo.create_dispute(
            booking_id=payload.booking_id,
            user_id=user_id,
            reason=payload.reason,
        )

        self.notifications.dispute_opened(dispute, user_id)

        return dispute


    def list_disputes_for_user(self, user_id: uuid.UUID):
        """
        User should see all disputes they opened.
        This method does not return disputes on their owned machines;
        that filtering is performed at the service level in routes if needed.
        """
        return self.repo.list_for_user(user_id)

    def list_disputes_for_booking(self, booking_id: uuid.UUID):
        return self.repo.list_for_booking(booking_id)

    def list_open_for_admin(self):
        return self.repo.list_open_for_admin()


    def set_status(
        self,
        dispute_id: uuid.UUID,
        *,
        new_status: DisputeStatus,
        resolution_notes: Optional[str] = None
    ):
        """
        Admin-only status transitions.
        Allowed transitions:
        OPEN -> IN_REVIEW
        IN_REVIEW -> NEEDS_INFO
        NEEDS_INFO -> IN_REVIEW
        """
        dispute = self._get_dispute_or_raise(dispute_id)

        #From OPEN -> IN_REVIEW -> NEEDS_INFO -> IN_REVIEW
        allowed = {
            (DisputeStatus.OPEN, DisputeStatus.IN_REVIEW),
            (DisputeStatus.IN_REVIEW, DisputeStatus.NEEDS_INFO),
            (DisputeStatus.NEEDS_INFO, DisputeStatus.IN_REVIEW),
        }

        if (dispute.status, new_status) not in allowed:
            raise ValueError("Invalid dispute status transition")

        updated = self.repo.update_status(
            dispute_id,
            new_status,
            resolution_notes=resolution_notes,
            resolved_at=None,
        )
        return updated


    def resolve_dispute(
        self,
        dispute_id: uuid.UUID,
        payload: DisputeResolution,
    ):
        """
        Admin-only.
        Decisions:
        -refund
        -deny
        When refund:
        call -> PaymentsPublic.refund_for_booking()
        """
        dispute = self._get_dispute_or_raise(dispute_id)

        if dispute.status not in {
            DisputeStatus.IN_REVIEW,
            DisputeStatus.NEEDS_INFO,
        }:
            raise ValueError("Dispute must be in-review or needs-info to be resolved")

        booking = self._get_booking_or_raise(dispute.booking_id)

        now = datetime.now(timezone.utc)

        if payload.decision == "refund":
            if payload.refund_amount is None or payload.refund_amount <= 0:
                raise ValueError("refund_amount must be > 0 for refund decisions")

            #Always refunds the full captured or held amount (from PaymentsPublic).
            #PaymentService.refund() implementation.
            #Extend PaymentsPublic for partial refund
            _ = self.payments_public.refund_for_booking(
                booking_id=booking.id,
                reason="dispute_resolution",
            )

            updated = self.repo.update_status(
                dispute_id,
                DisputeStatus.RESOLVED_REFUNDED,
                resolution_notes=payload.resolution_notes,
                resolved_at=now,
            )

            self.notifications.dispute_resolved(dispute, dispute.user) #consider: pass decision
            
            return updated

        #Deny
        elif payload.decision == "deny":
            updated = self.repo.update_status(
                dispute_id,
                DisputeStatus.RESOLVED_DENIED,
                resolution_notes=payload.resolution_notes,
                resolved_at=now,
            )

            self.notifications.dispute_resolved(dispute, dispute.user) #consider: pass decision
            
            return updated

        else:
            raise ValueError("Unsupported decision type")


    def close_dispute(self, dispute_id: uuid.UUID):
        """
        Admin-only. Closes a dispute after it has been resolved.
        """
        dispute = self._get_dispute_or_raise(dispute_id)

        if dispute.status not in {
            DisputeStatus.RESOLVED_REFUNDED,
            DisputeStatus.RESOLVED_DENIED,
        }:
            raise ValueError("Only resolved disputes can be closed")

        updated = self.repo.update_status(
            dispute_id,
            DisputeStatus.CLOSED,
            resolution_notes=dispute.resolution_notes,
            resolved_at=dispute.resolved_at,
        )
        return updated


def get_disputes_service(
    db: Session = Depends(get_db),
    bookings_public: BookingsPublic = Depends(get_bookings_public),
    payments_public: PaymentsPublic = Depends(get_payments_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> DisputeService:
    repo = DisputeRepository(db)
    return DisputeService(
        db=db,
        repo=repo,
        bookings_public=bookings_public,
        payments_public=payments_public,
        notifications_public=notifications_public,
    )