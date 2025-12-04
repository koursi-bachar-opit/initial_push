from uuid import UUID
from fastapi import HTTPException, status

from .repository import ComplianceRepository
from .schemas import WipeAttestationCreate, WipeAttestationUpdateStatus
from .models import WipeReviewStatus

from sqlalchemy.orm import Session

from app.machines.public import MachinesPublic, get_machines_public
from app.providers.public import ProvidersPublic, get_providers_public

from app.database import get_db
from fastapi import Depends

from app.notifications.public import NotificationsPublic, get_notifications_public

#consider: auto collect wipe and attestation
class ComplianceService:
    def __init__(
        self,
        db: Session,
        repo: ComplianceRepository,
        machines_public: MachinesPublic,
        providers_public: ProvidersPublic,
        notifications_public: NotificationsPublic,
    ):
        self.db = db
        self.repo = repo
        self.machines_public = machines_public
        self.providers_public = providers_public
        self.notifications = notifications_public

    def simulate_wipe_for_booking(self, booking):
        """
        Automatically simulate a wipe + create the attestation.
        """
        #if already exists, return it (idempotent)
        att = self.repo.get_by_booking(self.db, booking.id)
        if att:
            return att

        machine = booking.listing.machine

        #construct fake attestation
        create_data = WipeAttestationCreate(
            booking_id=booking.id,
            machine_id=machine.id,
            method="simulated-secure-erase",
            evidence_uri=f"mock://wipe/{booking.id}.log",
            notes="Simulated wipe completed successfully.",
        )

        return self.repo.create(
            db=self.db,
            booking_id=create_data.booking_id,
            machine_id=create_data.machine_id,
            method=create_data.method,
            evidence_uri=create_data.evidence_uri,
            notes=create_data.notes,
        )


    # Booking enforcement
    def require_attestation_for_booking(self, booking):
        att = self.repo.get_by_booking(self.db, booking.id)
        if not att:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Booking cannot be completed until a wipe attestation exists.",
            )
        return att
    

    #Provider submission
    def submit_attestation(self, provider_id: UUID, data: WipeAttestationCreate):
        machine = self.machines_public.get_machine(data.machine_id)
        if machine is None:
            raise HTTPException(404, "Machine not found")

        #provider must own the machine
        if machine.provider_id != provider_id:
            raise HTTPException(403, "You do not own this machine")

        #enforce 1 -> 1
        if self.repo.get_by_booking(self.db, data.booking_id):
            raise HTTPException(400, "Wipe attestation already exists for this booking")

        att = self.repo.create(
            db=self.db,
            booking_id=data.booking_id,
            machine_id=data.machine_id,
            method=data.method,
            evidence_uri=data.evidence_uri,
            notes=data.notes,
        )

        #self.notifications.wipe_proof_submitted(provider, booking, att) #consider: provider and booking errors
        
        return att

    #Admin review
    def admin_review(self, attestation_id: UUID, data: WipeAttestationUpdateStatus):
        updated = self.repo.update_status(self.db, attestation_id, data.status)
        if not updated:
            raise HTTPException(404, "Attestation not found")
        return updated

    #Queries
    def get_attestation_by_booking(self, booking):
        return self.repo.get_by_booking(self.db, booking.id)

    def list_machine_attestations(self, machine_id: UUID):
        return self.repo.list_machine_attestations(self.db, machine_id)

    def list_all_attestations(self):
        return self.repo.list_all(self.db)


def get_compliance_service(
    db: Session = Depends(get_db),
    machines_public: MachinesPublic = Depends(get_machines_public),
    providers_public: ProvidersPublic = Depends(get_providers_public),
    notifications_public: NotificationsPublic = Depends(get_notifications_public),
) -> ComplianceService:
    repo = ComplianceRepository()
    return ComplianceService(
        db=db,
        repo=repo,
        machines_public=machines_public,
        providers_public=providers_public,
        notifications_public=notifications_public,
    )