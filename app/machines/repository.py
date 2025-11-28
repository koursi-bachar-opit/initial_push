from uuid import UUID
from sqlalchemy.orm import Session
from .models import Machine
from .schemas import MachineCreate

class MachineRepository:
    def create_machine(self, db: Session, machine_data: MachineCreate):
        #payload for machine creation
        db_machine = Machine(
            provider_id=machine_data.provider_id,
            hostname=machine_data.hostname,
            location_region=machine_data.location_region,
            gpu_model=machine_data.gpu_model,
            gpu_count=machine_data.gpu_count,
            vram_gb=machine_data.vram_gb,
            cpu_model=machine_data.cpu_model,
            cpu_cores=machine_data.cpu_cores,
            ram_gb=machine_data.ram_gb,
            storage_gb=machine_data.storage_gb,
            network_mbps=machine_data.network_mbps,
            notes=machine_data.notes,
        )
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        return db_machine

    def get_machine(self, db: Session, machine_id: UUID) -> Machine | None:
        #get a machine by ID 
        return (
            db.query(Machine)
            .filter(Machine.id == machine_id)
            .first()
        )

    def list_machines_for_provider(self, db: Session, provider_id: UUID) -> list[Machine]:
        #query machines for specific provider
        return (
            db.query(Machine)
            .filter(Machine.provider_id == provider_id)
            .all()
        )

    def provider_owns_machine(self, db: Session, provider_id: UUID, machine_id: UUID) -> bool:
        #filter for machine provider machines
        return (
            db.query(Machine)
            .filter(
                Machine.id == machine_id,
                Machine.provider_id == provider_id,
            )
            .count()
            > 0
        )