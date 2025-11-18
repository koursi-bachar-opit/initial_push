"""
Enhanced user factories with role-based creation and config awareness.
"""
from app.repositories import user_repository
from app.models import UserRole
from test_config import TestConfig


# Keep the original pure factory functions
def create_user(db_session, email: str, role: str):
    """Pure factory - creates user with given email and role."""
    return user_repository.create_user(
        db=db_session,
        supabase_id=email,
        email=email,
        role=getattr(UserRole, role.upper()),
    )


def auth_headers_for(email: str, role: str):
    """Pure factory - creates auth headers for given email and role."""
    return {"Authorization": f"Bearer {role}:{email}"}


# New config-aware helper functions
def create_user_by_role(db_session, role="buyer"):
    """Config-aware: Create user with standardized test credentials."""
    email = getattr(TestConfig, f"{role.upper()}_EMAIL")
    return create_user(db_session, email, role)


def auth_headers_by_role(role):
    """Config-aware: Get auth headers for standardized test roles."""
    email = getattr(TestConfig, f"{role.upper()}_EMAIL")
    return auth_headers_for(email, role)


def create_admin_user(db_session):
    """Convenience function for creating admin user."""
    return create_user_by_role(db_session, "admin")


def create_provider_user(db_session):
    """Convenience function for creating provider user."""
    return create_user_by_role(db_session, "provider")


def create_buyer_user(db_session):
    """Convenience function for creating buyer user."""
    return create_user_by_role(db_session, "buyer")