from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

from app.machines.schemas import MachineRead


class ListingCreate(BaseModel):
    """Payload sent when creating a new listing."""
    machine_id: UUID
    title: str = Field(min_length=1)
    price: float = Field(ge=0)


class ListingRead(ListingCreate):
    id: UUID
    machine: Optional[MachineRead] = None

    model_config = ConfigDict(from_attributes=True)