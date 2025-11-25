from typing import Protocol
from sqlalchemy.orm import Session
from uuid import UUID

from fastapi import Depends
from app.database import get_db

from .service import BookingsService, get_bookings_service


class BookingsPublic(Protocol):
    """
    Public interface to interact with the Bookings domain.
    """
    def get_booking(self, booking_id: UUID):
        ...

    def is_active(self, booking) -> bool:
        ...

    def is_confirmed(self, booking) -> bool:
        ...

    def is_requested(self, booking) -> bool:
        ...

    def is_cancelled(self, booking) -> bool:
        ...

    def is_completed(self, booking) -> bool:
        ...

    def is_cancellable(self, booking) -> bool:
        ...


class BookingsPublicImpl:
    """
    Concrete implementation of the public facade.
    """
    def __init__(self, service: BookingsService):
        self.service = service

    def get_booking(self, booking_id: UUID):
        return self.service.get_booking_readonly(booking_id)

    def is_active(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.ACTIVE

    def is_confirmed(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.CONFIRMED

    def is_requested(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.REQUESTED
    
    def is_cancelled(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.CANCELLED
    
    def is_completed(self, booking) -> bool:
        return booking.status == self.service.BookingStatus.COMPLETED

    def is_cancellable(self, booking) -> bool:
        return booking.status in {
            self.service.BookingStatus.REQUESTED,
            self.service.BookingStatus.CONFIRMED,
        }


def get_bookings_public(
    service: BookingsService = Depends(get_bookings_service),
) -> BookingsPublic:
    return BookingsPublicImpl(service)