from typing import Protocol
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from .repository import UserRepository
from .models import User, UserRole


class UsersPublic(Protocol):
    """
    Public interface for interacting with the Users domain.
    """
    def get_user_by_supabase_id(self, sub: str) -> User | None:
        ...

    def get_user(self, user_id: UUID) -> User | None:
        ...

    def get_role(self, user: User) -> UserRole:
        ...

    def create_user(self, email: str, supabase_id: str | None, role: UserRole) -> User:
        ...

    #def get_or_create_user_by_supabase_id(self, sub: str, email: str, role: UserRole) -> User:
    #    ...

    def is_buyer_role(self, user: User) -> bool:
        ...
    
    def is_provider_role(self, user: User) -> bool:
        ...

    def is_admin_role(self, user: User) -> bool:
        ...

    #
    def get_or_create_user_by_supabase_id(self, sub: str, email: str, role: str | None) -> User:
        ...

    def _ensure_provider_profile_exists(self, user: User) -> None:
        ...
    #
    

#refactor
from app.providers.models import ProviderProfile
from app.providers.schemas import ProviderProfileCreate
#refactor

class UsersPublicImpl:
    """
    Concrete implementation of the public interface.
    Wraps the UserRepository, providing a stable boundary.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository()

    def get_user_by_supabase_id(self, sub: str) -> User | None:
        return self.repo.get_user_by_supabase_id(self.db, sub)

    def get_user(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_role(self, user: User) -> UserRole:
        return user.role

    def create_user(self, email: str, supabase_id: str | None, role: UserRole) -> User:
        return self.repo.create_user(self.db, email=email, supabase_id=supabase_id, role=role)
    
    #refactor
    def get_or_create_user_by_supabase_id(self, sub: str, email: str, role: str | None) -> User:
        user = self.repo.get_or_create_user_by_supabase_id(self.db, sub=sub, email=email, role=role)
        
        # Auto-create ProviderProfile for new provider users
        if user.role == UserRole.PROVIDER:
            self._ensure_provider_profile_exists(user)
        
        return user
    
    def _ensure_provider_profile_exists(self, user: User) -> None:
        """Ensure a ProviderProfile exists for provider users - using direct DB access to avoid circular imports"""
        try:
            # Check if profile already exists using direct DB query
            existing_profile = self.db.query(ProviderProfile).filter(
                ProviderProfile.user_id == user.id
            ).first()
            
            if not existing_profile:
                # Create provider profile directly
                profile = ProviderProfile(
                    user_id=user.id,
                    payout_account_ref=None,
                    verification_status="pending"
                )
                self.db.add(profile)
                self.db.commit()
                self.db.refresh(profile)  # Refresh to get the profile ID
                print(f"Created provider profile for user: {user.email}")
                
                #AUTO-CREATE VERIFICATION REQUEST
                from app.providers.models import Verification, VerificationSubject, VerificationStatus
                verification = Verification(
                    subject_type=VerificationSubject.PROVIDER,
                    subject_id=profile.id,  # Use the profile ID
                    status=VerificationStatus.PENDING,
                    notes="Auto-created on provider registration"
                )
                self.db.add(verification)
                self.db.commit()
                print(f"Created auto-verification request for provider: {user.email}")
                
        except Exception as e:
            # Log the error but don't break user creation
            print(f"Warning: Failed to create provider profile for user {user.id}: {e}")
            self.db.rollback()  # Important: rollback on error
    #refactor

    #
    #def get_or_create_user_by_supabase_id(self, sub: str, email: str, role: UserRole) -> User:
    #    return self.repo.get_or_create_user_by_supabase_id(self.db, sub=sub, email=email, role=role)
    #
    
    def is_buyer_role(self, user: User) -> bool:
        return user.role == UserRole.BUYER
    
    def is_provider_role(self, user: User) -> bool:
        return user.role == UserRole.PROVIDER
    
    def is_admin_role(self, user: User) -> bool:
        return user.role == UserRole.ADMIN


def get_users_public(
    db: Session = Depends(get_db),
) -> UsersPublic:
    """
    FastAPI DI provider for UsersPublic.
    """
    return UsersPublicImpl(db)