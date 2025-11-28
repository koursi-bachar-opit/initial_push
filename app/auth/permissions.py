from fastapi import Depends
from uuid import UUID

from app.auth.auth import get_current_user
from app.auth.public import AuthPublic, get_auth_public


def require_buyer_role(
    current_user = Depends(get_current_user),
    auth_public: AuthPublic = Depends(get_auth_public),
):
    """
    Dependency ensuring the current user has the BUYER role.
    """
    auth_public.ensure_buyer(current_user.id)
    return current_user


def require_provider_role(
    current_user = Depends(get_current_user),
    auth_public: AuthPublic = Depends(get_auth_public),
):
    """
    Dependency ensuring the current user has the PROVIDER role.
    """
    auth_public.ensure_provider(current_user.id)
    return current_user