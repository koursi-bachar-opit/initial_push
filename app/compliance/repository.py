from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from .models import WipeAttestation, WipeReviewStatus


class ComplianceRepository:
    def create(self, db: Session, *, booking_id: UUID, machine_id: UUID, 
               method: str, evidence_uri: str, notes: str):

        att = WipeAttestation(
            booking_id=booking_id,
            machine_id=machine_id,
            method=method,
            evidence_uri=evidence_uri,
            notes=notes,
        )
        db.add(att)
        db.commit()
        db.refresh(att)
        return att

    def get_by_booking(self, db: Session, booking_id: UUID):
        stmt = select(WipeAttestation).where(
            WipeAttestation.booking_id == booking_id
        )
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def list_machine_attestations(self, db: Session, machine_id: UUID):
        stmt = select(WipeAttestation).where(
            WipeAttestation.machine_id == machine_id
        ).order_by(WipeAttestation.attested_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()

    def list_all(self, db: Session):
        stmt = select(WipeAttestation).order_by(WipeAttestation.attested_at.desc())
        result = db.execute(stmt)
        return result.scalars().all()

    def update_status(self, db: Session, attestation_id: UUID, 
                      status: WipeReviewStatus):
        stmt = select(WipeAttestation).where(WipeAttestation.id == attestation_id)
        result = db.execute(stmt)
        att = result.scalar_one_or_none()
        
        if not att:
            return None

        att.status = status
        db.commit()
        db.refresh(att)
        return att

# from sqlalchemy.orm import Session
# from uuid import UUID

# from .models import WipeAttestation, WipeReviewStatus
# from .schemas import WipeAttestationCreate


# class ComplianceRepository:
#     def __init__(self, db: Session):
#         self.db = db

#     def create(self, data: WipeAttestationCreate, provider_id: UUID):
#         """"""
#         from app.providers.models import ProviderProfile
#         # Resolve provider profile by user_id
#         profile = (
#             self.db.query(ProviderProfile)
#             .filter(ProviderProfile.user_id == provider_id)
#             .first()
#         )
#         if not profile:
#             # In tests we always create a profile in the factories;
#             # in real code you might want a domain-specific exception here.
#             raise ValueError(
#                 f"ProviderProfile not found for user_id={provider_id}"
#             )
#         """"""
        
#         att = WipeAttestation(
#             booking_id=data.booking_id,
#             machine_id=data.machine_id,
#             provider_id=profile.id, #NEW LINE: use ProviderProfile.id for FK
#             method=data.method,
#             evidence_uri=data.evidence_uri,
#             notes=data.notes,
#         )
#         self.db.add(att)
#         self.db.commit()
#         self.db.refresh(att)
#         return att

#     def get_by_booking(self, booking_id: UUID):
#         return (
#             self.db.query(WipeAttestation)
#             .filter(WipeAttestation.booking_id == booking_id)
#             .first()
#         )

#     def list_machine_attestations(self, machine_id: UUID):
#         return (
#             self.db.query(WipeAttestation)
#             .filter(WipeAttestation.machine_id == machine_id)
#             .order_by(WipeAttestation.created_at.desc())
#             .all()
#         )

#     def list_all(self):
#         return self.db.query(WipeAttestation).order_by(WipeAttestation.created_at.desc()).all()

#     def update_status(self, attestation_id: UUID, status: WipeReviewStatus, notes: str | None):
#         att = self.db.query(WipeAttestation).filter(WipeAttestation.id == attestation_id).first()
#         if not att:
#             return None

#         att.admin_review_status = status
#         att.admin_notes = notes
#         self.db.commit()
#         self.db.refresh(att)
#         return att