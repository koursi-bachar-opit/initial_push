from typing import Protocol
from sqlalchemy.orm import Session
from uuid import UUID

from fastapi import Depends
from app.database import get_db

from app.bookings.service import BookingsService, get_bookings_service #consider


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

    def is_ready_for_capture(self, booking) -> bool:
        ...

    def get_org_bookings_in_period(self, org_id, period_start, period_end):
        ...


class BookingsPublicImpl:
    """
    Concrete implementation of the public facade.
    """
    def __init__(self, service: BookingsService):
    #def __init__(self, service: "BookingsService"):
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
    
    #
    def is_ready_for_capture(self, booking) -> bool:
        return (
            booking.status == self.service.BookingStatus.COMPLETED 
            and booking.actual_price_charged is not None
        )
    #

    def get_org_bookings_in_period(self, org_id, period_start, period_end): #consider: identical naming across public and service
        return self.service.get_org_bookings_in_period(org_id, period_start, period_end)


def get_bookings_public(
    service: BookingsService = Depends(get_bookings_service),
) -> BookingsPublic:
    return BookingsPublicImpl(service)