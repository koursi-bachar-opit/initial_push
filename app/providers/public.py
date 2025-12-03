from fastapi import Depends
from sqlalchemy.orm import Session

from .service import (
    ProviderProfileService,
    VerificationService,
    get_provider_profile_service,
    get_verification_service,
)
from .models import ProviderVerificationStatus

from app.database import get_db


class ProvidersPublic:
    """
    Public interface used by other domains:
    - ListingsService (to check provider verification)
    - MachinesService (to ensure provider owns verified profile)
    - PaymentsService (future payout eligibility)
    - ComplianceService (verification linkage)
    """
    def __init__(
        self,
        profile_service: ProviderProfileService,
        verification_service: VerificationService,
    ):
        self.profile_service = profile_service
        self.verification_service = verification_service


    def get_profile_by_user(self, user_id):
        return self.profile_service.repo.get_by_user_id(user_id)

    def require_verified_provider(self, user_id):
        return self.profile_service.require_verified(user_id)

    def is_verified(self, user_id) -> bool:
        profile = self.get_profile_by_user(user_id)
        return (
            profile is not None
            and profile.verification_status == ProviderVerificationStatus.verified
        )

    def list_verifications(self, subject_type, subject_id):
        return self.verification_service.list_verifications(subject_type, subject_id)


def get_providers_public(
    db: Session = Depends(get_db),
    profile_service: ProviderProfileService = Depends(get_provider_profile_service),
    verification_service: VerificationService = Depends(get_verification_service),
) -> ProvidersPublic:
    return ProvidersPublic(
        profile_service=profile_service,
        verification_service=verification_service,
    )