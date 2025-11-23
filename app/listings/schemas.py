from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.machines.schemas import MachineRead


class ListingCreate(BaseModel):
    """Payload sent when creating a new listing."""
    machine_id: int
    title: str = Field(min_length=1)
    price: float = Field(ge=0)


class ListingRead(ListingCreate):
    id: int
    machine: Optional[MachineRead] = None

    model_config = ConfigDict(from_attributes=True)