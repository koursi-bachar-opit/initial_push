from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class MachineCreate(BaseModel):
    provider_id: int | None = None
    hostname: str | None = None
    location_region: str | None = None
    gpu_model: str | None = None
    gpu_count: int | None = None
    vram_gb: int | None = None
    cpu_model: str | None = None
    cpu_cores: int | None = None
    ram_gb: int | None = None
    storage_gb: int | None = None
    network_mbps: int | None = None
    notes: str | None = None


class MachineRead(MachineCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)