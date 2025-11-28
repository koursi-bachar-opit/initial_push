from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class MachineCreate(BaseModel):
    provider_id: Optional[UUID] = None
    hostname: Optional[str] = None
    location_region: Optional[str] = None

    gpu_model: Optional[str] = None
    gpu_count: Optional[int] = None
    vram_gb: Optional[int] = None

    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    ram_gb: Optional[int] = None

    storage_gb: Optional[int] = None
    network_mbps: Optional[int] = None
    notes: Optional[str] = None


class MachineRead(MachineCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)