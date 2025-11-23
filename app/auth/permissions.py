from app import models

def booking_has_valid_relationships(booking):
    if booking.listing is None:
        return False
    if booking.listing.machine is None:
        return False
    if booking.listing.machine.provider_id is None:
        return False
    return True


def can_confirm_booking(user, booking):
    if not booking_has_valid_relationships(booking):
        return False

    if user.role == models.UserRole.ADMIN:
        return True

    provider_id = booking.listing.machine.provider_id

    if user.role == models.UserRole.PROVIDER and user.id == provider_id:
        return True

    return False


def can_cancel_booking(user, booking):
    if not booking_has_valid_relationships(booking):
        return False

    #Buyer can cancel their own bookings before start
    if user.role == models.UserRole.BUYER and user.id == booking.buyer_user_id:
        return True

    #Provider can cancel bookings for machines they own before start
    provider_id = booking.listing.machine.provider_id
    if user.role == models.UserRole.PROVIDER and user.id == provider_id:
        return True

    #Admin can cancel always
    if user.role == models.UserRole.ADMIN:
        return True

    return False


def can_start_session(user, booking):
    if not booking_has_valid_relationships(booking):
        return False

    if user.role == models.UserRole.ADMIN:
        return True

    provider_id = booking.listing.machine.provider_id
    if user.role == models.UserRole.PROVIDER and user.id == provider_id:
        return True

    #Buyers never allowed
    return False


def can_end_session(user, booking):
    if not booking_has_valid_relationships(booking):
        return False

    if user.role == models.UserRole.ADMIN:
        return True

    provider_id = booking.listing.machine.provider_id
    if user.role == models.UserRole.PROVIDER and user.id == provider_id:
        return True

    return False