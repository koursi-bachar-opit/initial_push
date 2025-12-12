from typing import Protocol
from uuid import UUID

from .service import ComplianceService, get_compliance_service
from .models import WipeAttestation

from fastapi import Depends


class CompliancePublic(Protocol):
    def simulate_wipe_for_booking(self, booking) -> WipeAttestation: 
        ...

    def get_attestation_by_booking(self, booking) -> WipeAttestation | None: 
        ...

    def require_attestation_for_booking(self, booking) -> WipeAttestation: 
        ...


class CompliancePublicImpl(CompliancePublic):
    def __init__(self, service: ComplianceService):
        self.service = service

    def simulate_wipe_for_booking(self, booking):
        return self.service.simulate_wipe_for_booking(booking)

    def get_attestation_by_booking(self, booking):
        return self.service.get_attestation_by_booking(booking)

    def require_attestation_for_booking(self, booking):
        return self.service.require_attestation_for_booking(booking)


def get_compliance_public(
    service: ComplianceService = Depends(get_compliance_service),
) -> CompliancePublic:
    return CompliancePublicImpl(service)