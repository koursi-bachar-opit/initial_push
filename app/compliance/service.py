from uuid import UUID

from .repository import ComplianceRepository
from .schemas import WipeAttestationCreate, WipeAttestationUpdateStatus, WipeVerificationPublic
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

    #update tests
    def simulate_wipe_for_booking(self, booking):
        """
        Automatically simulate a wipe + create the attestation.
        """
        #If already exists, return it (idempotent)
        if booking.wipe_attestation:
            return booking.wipe_attestation

        #Construct fake attestation
        create_data = WipeAttestationCreate(
            booking_id=booking.id,
            machine_id=booking.listing.machine.id,
            method="simulated-secure-erase",
            evidence_uri=f"mock://wipe/{booking.id}.log",
            notes="Simulated wipe completed successfully.",
        )

        #Create the attestation via repository
        attestation = self.repo.create(
            db=self.db,
            booking_id=create_data.booking_id,
            machine_id=create_data.machine_id,
            method=create_data.method,
            evidence_uri=create_data.evidence_uri,
            notes=create_data.notes,
        )
        
        #consider: Update status to VERIFIED for simulation
        #use the repository's update_status method
        updated_attestation = self.repo.update_status(
            db=self.db,
            attestation_id=attestation.id,
            status=WipeReviewStatus.VERIFIED
        )
        
        return updated_attestation
    # def simulate_wipe_for_booking(self, booking):
    #     """
    #     Automatically simulate a wipe + create the attestation.
    #     """
    #     #if already exists, return it (idempotent)
    #     if booking.wipe_attestation:
    #         return booking.wipe_attestation

    #     #construct fake attestation
    #     create_data = WipeAttestationCreate(
    #         booking_id=booking.id,
    #         machine_id=booking.listing.machine.id,
    #         method="simulated-secure-erase",
    #         evidence_uri=f"mock://wipe/{booking.id}.log",
    #         notes="Simulated wipe completed successfully.",
    #     )

    #     return self.repo.create(
    #         db=self.db,
    #         booking_id=create_data.booking_id,
    #         machine_id=create_data.machine_id,
    #         method=create_data.method,
    #         evidence_uri=create_data.evidence_uri,
    #         notes=create_data.notes,
    #     )
    #update tests


    #update tests (HTTP exception to ValueError)
    # Booking enforcement
    def require_attestation_for_booking(self, booking):
        att = self.repo.get_by_booking(self.db, booking.id)
        if not att:
            raise ValueError("Booking cannot be completed until a wipe attestation exists.")
        
        return att
    

    #Provider submission
    def submit_attestation(self, provider_id: UUID, data: WipeAttestationCreate):
        machine = self.machines_public.get_machine(data.machine_id)
        if machine is None:
            raise ValueError("Machine not found")

        #provider must own the machine
        if machine.provider_id != provider_id:
            raise ValueError("You do not own this machine")

        #enforce 1 -> 1
        if self.repo.get_by_booking(self.db, data.booking_id):
            raise ValueError("Wipe attestation already exists for this booking")

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
            raise ValueError("Attestation not found")
        return updated
    #update tests


    #Queries
    def get_attestation_by_booking(self, booking):
        return self.repo.get_by_booking(self.db, booking.id)

    def list_machine_attestations(self, machine_id: UUID):
        return self.repo.list_machine_attestations(self.db, machine_id)

    def list_all_attestations(self):
        return self.repo.list_all(self.db)
    

    #update tests
    def get_buyer_verification(self, booking_id: UUID, user_id: UUID):
        """
        Buyer gets verification status only.
        Checks ownership internally using relationships.
        """
        #Get attestation with booking relationship
        attestation = self.repo.get_by_booking_with_relations(self.db, booking_id)
        if not attestation:
            raise ValueError("No booking attestation found.")
        
        #Check ownership using relationship
        if attestation.booking.buyer_user_id != user_id:
            raise ValueError("Not your booking") #raise as HTTPException in routes
        
        #Map detailed method to user-friendly summary
        method_summary_map = {
            "simulated-secure-erase": "Secure erase",
            "zero-fill": "Zero-fill wipe",
            "cryptographic-erase": "Cryptographic erase",
            "physical-destruction": "Physical destruction"
        }
        
        summary = method_summary_map.get(
            attestation.method, 
            attestation.method.split("-")[0].title() + " wipe"
        )
        
        return WipeVerificationPublic(
            is_verified=attestation.status == WipeReviewStatus.VERIFIED,
            status=attestation.status,
            verified_at=attestation.attested_at if attestation.status == WipeReviewStatus.VERIFIED else None,
            method_summary=summary
        )
    
    def get_provider_attestation(self, provider_id: UUID, booking_id: UUID):
        """Provider gets full attestation for their machines"""
        attestation = self.repo.get_by_booking_with_relations(self.db, booking_id)
        if not attestation:
            raise ValueError("No wipe attestation found")
        
        # Verify provider owns the machine (using relationship)
        if attestation.machine.provider_id != provider_id:
            raise ValueError("Not authorized")
            
        return attestation  # Full details with relationships
    
    def get_admin_attestation(self, booking_id: UUID):
        """Admin gets full attestation"""
        attestation = self.repo.get_by_booking_with_relations(self.db, booking_id)
        if not attestation:
            raise ValueError("No wipe attestation found")
        return attestation
    #update tests


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