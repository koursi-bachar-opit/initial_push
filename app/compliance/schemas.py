from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict


class WipeReviewStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class WipeAttestationBase(BaseModel):
    method: str
    evidence_uri: str | None = None
    notes: str | None = None


class WipeAttestationCreate(WipeAttestationBase):
    booking_id: UUID
    machine_id: UUID


class WipeAttestationRead(WipeAttestationBase):
    id: UUID
    booking_id: UUID
    machine_id: UUID
    attested_at: datetime
    status: WipeReviewStatus

    model_config = ConfigDict(from_attributes=True)


class WipeAttestationUpdateStatus(BaseModel):
    status: WipeReviewStatus