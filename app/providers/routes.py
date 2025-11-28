from fastapi import APIRouter, Depends, HTTPException

from app.auth.auth import get_current_user
from app.auth.permissions import require_admin_role

from .schemas import (
    ProviderProfileCreate,
    ProviderProfileUpdate,
    ProviderProfileRead,
    VerificationCreate,
    VerificationUpdateStatus,
    VerificationRead,
)

from .public import ProvidersPublic, get_providers_public
from app.users.models import User  #matches your pattern in bookings/routes.py


router = APIRouter()


#Provider profiles
@router.post("/me", response_model=ProviderProfileRead, status_code=201)
def create_my_provider_profile(
    payload: ProviderProfileCreate,
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    try:
        return providers.profile_service.create_profile(user.id, payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/me", response_model=ProviderProfileRead)
def update_my_provider_profile(
    payload: ProviderProfileUpdate,
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    profile = providers.get_profile_by_user(user.id)
    if not profile:
        raise HTTPException(404, "Provider profile not found.")
    try:
        return providers.profile_service.update_profile(user.id, profile.id, payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/me", response_model=ProviderProfileRead)
def get_my_provider_profile(
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    profile = providers.get_profile_by_user(user.id)
    if not profile:
        raise HTTPException(404, "Provider profile not found.")
    return profile


#Verification (user requests verification)
@router.post("/me/verification", response_model=VerificationRead, status_code=201)
def request_provider_verification(
    payload: VerificationCreate,
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    try:
        return providers.verification_service.create_verification_request(
            user.id, payload
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/me/verifications", response_model=list[VerificationRead])
def list_my_verifications(
    user: User = Depends(get_current_user),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    profile = providers.get_profile_by_user(user.id)
    if not profile:
        raise HTTPException(404, "Provider profile not found.")
    return providers.list_verifications("provider", profile.id)


#Admin review of verification entries
@router.post("/verification/{verification_id}/review", response_model=VerificationRead)
def admin_review_verification(
    verification_id: str,
    payload: VerificationUpdateStatus,
    admin: User = Depends(require_admin_role),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    try:
        return providers.verification_service.admin_update_verification(
            admin.id,
            verification_id,
            payload.status,
            payload.notes,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


#Admin: list verification events
@router.get("/verification/{subject_type}/{subject_id}", response_model=list[VerificationRead])
def admin_list_verifications_for_subject(
    subject_type: str,
    subject_id: str,
    admin: User = Depends(require_admin_role),
    providers: ProvidersPublic = Depends(get_providers_public),
):
    return providers.list_verifications(subject_type, subject_id)