from typing import List, Optional
from sqlalchemy.orm import Session

from . import models, schemas


class ProviderRepository:
    """
    Persistence layer for ProviderProfile + Verification.
    """
    def __init__(self, db: Session):
        self.db = db


    #ProviderProfile CRUD
    def get(self, profile_id) -> Optional[models.ProviderProfile]:
        return (
            self.db.query(models.ProviderProfile)
            .filter(models.ProviderProfile.id == profile_id)
            .first()
        )

    def get_by_user_id(self, user_id) -> Optional[models.ProviderProfile]:
        return (
            self.db.query(models.ProviderProfile)
            .filter(models.ProviderProfile.user_id == user_id)
            .first()
        )

    def create(
        self,
        user_id,
        data: schemas.ProviderProfileCreate,
    ) -> models.ProviderProfile:
        profile = models.ProviderProfile(
            user_id=user_id,
            payout_account_ref=data.payout_account_ref,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(
        self,
        profile: models.ProviderProfile,
        data: schemas.ProviderProfileUpdate,
    ) -> models.ProviderProfile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        self.db.commit()
        self.db.refresh(profile)
        return profile


    #Verification CRUD
    def get_verification(
        self,
        verification_id,
    ) -> Optional[models.Verification]:
        return (
            self.db.query(models.Verification)
            .filter(models.Verification.id == verification_id)
            .first()
        )

    def create_verification(
        self,
        data: schemas.VerificationCreate,
    ) -> models.Verification:
        verification = models.Verification(
            subject_type=data.subject_type,
            subject_id=data.subject_id,
            notes=data.notes,
        )
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification

    def update_verification(
        self,
        verification: models.Verification,
        new_status: models.VerificationStatus,
        notes: str | None,
        admin_user_id,
    ) -> models.Verification:
        verification.status = new_status
        verification.notes = notes
        verification.performed_by_admin_id = admin_user_id

        self.db.commit()
        self.db.refresh(verification)
        return verification

    def list_verifications_for(
        self, subject_type, subject_id
    ) -> List[models.Verification]:
        return (
            self.db.query(models.Verification)
            .filter(
                models.Verification.subject_type == subject_type,
                models.Verification.subject_id == subject_id,
            )
            .order_by(models.Verification.created_at.desc())
            .all()
        )
    
    def save_verification(
        self,
        verification: models.Verification,
    ) -> models.Verification:
        self.db.commit()
        self.db.refresh(verification)
        return verification