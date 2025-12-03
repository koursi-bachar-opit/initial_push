from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import Payment, PaymentType, PaymentStatus


class PaymentsRepository:
    """
    Payment persistence layer.
    """
    def create_payment(self, db: Session, payment: Payment) -> Payment:
        """
        Persist a newly created Payment ORM instance.
        """
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment


    def update_payment(self, db: Session, payment: Payment) -> Payment:
        """
        Commit and refresh an updated Payment instance.
        """
        db.commit()
        db.refresh(payment)
        return payment


    def get_payment_by_id(self, db: Session, payment_id: UUID) -> Optional[Payment]:
        """
        Fetch a Payment by primary key.
        """
        return db.get(Payment, payment_id)


    #consider: first non-id ascending order
    def list_payments_for_booking(self, db: Session, booking_id: UUID) -> List[Payment]:
        """
        Returns all payments for a given booking, ordered chronologically.
        """
        return (
            db.query(Payment)
            .filter(Payment.booking_id == booking_id)
            .order_by(Payment.created_at.asc())
            .all()
        )


    def get_latest_escrow(self, db: Session, booking_id: UUID) -> Optional[Payment]:
        """
        Retrieve the most recent escrow payment for a booking.
        Used before capture() or refund().
        """
        return (
            db.query(Payment)
            .filter(
                Payment.booking_id == booking_id,
                Payment.type == PaymentType.ESCROW
            )
            .order_by(Payment.created_at.desc())
            .first()
        )

    def get_by_processor_ref(self, db: Session, processor_ref: str) -> Optional[Payment]:
        """
        For webhook reconciliation: find a Payment by processor reference.
        """
        return (
            db.query(Payment)
            .filter(Payment.processor_ref == processor_ref)
            .first()
        )
    
    def list_payments_for_bookings(self, db: Session, booking_ids: list[UUID]):
        if not booking_ids:
            return []

        return (
            db.query(Payment)
            .filter(Payment.booking_id.in_(booking_ids))
            .order_by(Payment.created_at.asc())
            .all()
        )
