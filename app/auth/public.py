from typing import Protocol
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.users.public import UsersPublic, get_users_public

#refactor heavy logic or exception handling out of public 
class AuthPublic(Protocol):
    """
    Public interface for authentication and authorization checks.
    """
    def ensure_buyer(self, user_id: UUID) -> None:
        ...

    def ensure_provider(self, user_id: UUID) -> None:
        ...

    def ensure_admin(self, user_id: UUID) -> None:
        ...


class AuthPublicImpl:
    """
    This delegates role checks to UsersPublic.
    Keeps all user and role logic inside the Users domain.
    """
    def __init__(self, db: Session, users_public: UsersPublic):
        self.db = db
        self.users_public = users_public

    def _get_user_or_403(self, user_id: UUID):
        user = self.users_public.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )
        return user

    def ensure_buyer(self, user_id: UUID) -> None:
        user = self._get_user_or_403(user_id)
        if not self.users_public.is_buyer_role(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Buyer role required.",
            )

    def ensure_provider(self, user_id: UUID) -> None:
        user = self._get_user_or_403(user_id)
        if not self.users_public.is_provider_role(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Provider role required.",
            )
        
    def ensure_admin(self, user_id: UUID) -> None:
        user = self._get_user_or_403(user_id)
        if not self.users_public.is_admin_role(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required.",
            )


def get_auth_public(
    db: Session = Depends(get_db),
    users_public: UsersPublic = Depends(get_users_public),
) -> AuthPublic:
    return AuthPublicImpl(db=db, users_public=users_public)