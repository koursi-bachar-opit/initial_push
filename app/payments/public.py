from typing import Protocol, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
from fastapi import Depends

from .service import PaymentsService, get_payments_service
from .models import Payment


class PaymentsPublic(Protocol):
    """
    Public interface exposed to other domains.
    """
    def escrow_for_booking(
        self,
        db: Session,
        *,
        booking,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        ...

    def capture_for_booking(
        self,
        db: Session,
        *,
        booking,
    ) -> Payment:
        ...

    def refund_for_booking(
        self,
        db: Session,
        *,
        booking,
        reason: str | None = None,
    ) -> Payment:
        ...

    def list_for_booking(
        self,
        db: Session,
        booking,
    ) -> List[Payment]:
        ...

    def void_escrow_for_booking(
        self,
        db: Session,
        *,
        booking,
    ) -> Payment:
        ...

    def get_payments_for_bookings(self, db: Session, booking_ids):
        ...


class PaymentsPublicImpl(PaymentsPublic):
    def __init__(self, service: PaymentsService):
        self.service = service  #self.db public signature

    def escrow_for_booking(
        self,
        db: Session,
        *,
        booking,
        amount: Decimal,
        currency: str,
    ) -> Payment:
        return self.service.create_escrow(
            db,
            booking=booking,
            amount=amount,
            currency=currency,
        )

    def capture_for_booking(
        self,
        db: Session,
        *,
        booking,
    ) -> Payment:
        return self.service.capture(
            db,
            booking=booking,
        )

    def refund_for_booking(
        self,
        db: Session,
        *,
        booking,
        reason: str | None = None,
    ) -> Payment:
        return self.service.refund(
            db,
            booking=booking,
            reason=reason,
        )

    def list_for_booking(
        self,
        db: Session,
        booking,
    ):
        return self.service.list_for_booking(db, booking)
    
    def void_escrow_for_booking(
        self,
        db: Session,
        *,
        booking,
    ) -> Payment:
        return self.service.void_escrow(db, booking=booking)
    
    def get_payments_for_bookings(self, db: Session, booking_ids):
        return self.service.get_payments_for_bookings(db, booking_ids)


def get_payments_public(
    service: PaymentsService = Depends(get_payments_service),
) -> PaymentsPublic:
    return PaymentsPublicImpl(service)