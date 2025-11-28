import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.disputes.models import Dispute, DisputeStatus


class DisputeRepository:
    """
    Repository handling all persistence operations for the Dispute domain.
    Responsibilities:
    -Create disputes
    -Fetch by ID
    -List disputes for user
    -List disputes for booking
    -List open disputes for admin review
    -Update dispute status and resolution fields
    """
    def __init__(self, session: Session):
        self.session = session


    def create_dispute(
        self,
        booking_id: uuid.UUID,
        user_id: uuid.UUID,
        reason: str
    ) -> Dispute:
        dispute = Dispute(
            booking_id=booking_id,
            opened_by_user_id=user_id,
            reason=reason,
            status=DisputeStatus.OPEN,
        )
        self.session.add(dispute)
        self.session.commit()
        self.session.refresh(dispute)
        return dispute


    def get_by_id(self, dispute_id: uuid.UUID) -> Optional[Dispute]:
        stmt = select(Dispute).where(Dispute.id == dispute_id)
        return self.session.scalar(stmt)


    #List queries
    def list_for_user(self, user_id: uuid.UUID) -> List[Dispute]:
        """
        Returns all disputes:
        - opened by the user
        - OR on bookings owned by the user as a provider
        NOTE: provider-ownership filtering is done at service layer
        using BookingsPublic -> Listing -> Machine.
        At repo level we only filter by opened_by_user_id.
        """
        stmt = (
            select(Dispute)
            .where(Dispute.opened_by_user_id == user_id)
            .order_by(Dispute.created_at.desc())
        )
        return list(self.session.scalars(stmt))

    def list_for_booking(self, booking_id: uuid.UUID) -> List[Dispute]:
        stmt = (
            select(Dispute)
            .where(Dispute.booking_id == booking_id)
            .order_by(Dispute.created_at.desc())
        )
        return list(self.session.scalars(stmt))

    def list_open_for_admin(self) -> List[Dispute]:
        stmt = (
            select(Dispute)
            .where(
                Dispute.status.in_(
                    [
                        DisputeStatus.OPEN,
                        DisputeStatus.IN_REVIEW,
                        DisputeStatus.NEEDS_INFO,
                    ]
                )
            )
            .order_by(Dispute.created_at.asc())
        )
        return list(self.session.scalars(stmt))


    #update operations
    def update_status(
        self,
        dispute_id: uuid.UUID,
        new_status: DisputeStatus,
        resolution_notes: Optional[str] = None,
        resolved_at: Optional[datetime] = None,
    ) -> Optional[Dispute]:
        stmt = (
            update(Dispute)
            .where(Dispute.id == dispute_id)
            .values(
                status=new_status,
                resolution_notes=resolution_notes,
                resolved_at=resolved_at,
            )
            .execution_options(synchronize_session="fetch")
        )

        self.session.execute(stmt)
        self.session.commit()

        return self.get_by_id(dispute_id)