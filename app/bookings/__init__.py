"""
Public interface for the Bookings domain module.
"""

from .service import BookingsService, get_bookings_service
from .repository import BookingRepository, booking_repository
from .schemas import (
    BookingRead,
    BookingRequest,
    BookingAdminCreate,
    BookingStatus,
)
from .models import Booking

__all__ = [
    # Service
    "BookingsService",
    "get_bookings_service",

    # Repository
    "booking_repository",
    "BookingRepository",

    # Schemas
    "BookingRequest",
    "BookingAdminCreate",
    "BookingRead",
    "BookingStatus",

    # Models
    "Booking",
]