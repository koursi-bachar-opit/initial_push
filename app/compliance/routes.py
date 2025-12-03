from fastapi import APIRouter, Depends
from uuid import UUID

from .schemas import (
    WipeAttestationCreate,
    WipeAttestationRead,
    WipeAttestationUpdateStatus,
)
from .service import ComplianceService, get_compliance_service
from app.auth.public import ensure_provider, ensure_admin


router = APIRouter()


#Provider submission
@router.post(
    "/attestations",
    response_model=WipeAttestationRead,
)
def submit_attestation(
    data: WipeAttestationCreate,
    current_user = Depends(ensure_provider),
    service: ComplianceService = Depends(get_compliance_service),
):
    provider_id = current_user.id
    return service.submit_attestation(provider_id, data)


#Admin review
@router.patch(
    "/attestations/{attestation_id}/review",
    response_model=WipeAttestationRead,
    dependencies=[Depends(ensure_admin)],
)
def review_attestation(
    attestation_id: UUID,
    data: WipeAttestationUpdateStatus,
    service: ComplianceService = Depends(get_compliance_service),
):
    return service.admin_review(attestation_id, data)


#Audit browsing (Admin)
@router.get(
    "/attestations",
    response_model=list[WipeAttestationRead],
    dependencies=[Depends(ensure_admin)],
)
def list_all(service: ComplianceService = Depends(get_compliance_service)):
    return service.list_all_attestations()


#Machine wipe log (Provider/Admin)
@router.get(
    "/machines/{machine_id}/attestations",
    response_model=list[WipeAttestationRead],
)
def machine_attestations(
    machine_id: UUID,
    service: ComplianceService = Depends(get_compliance_service),
):
    return service.list_machine_attestations(machine_id)