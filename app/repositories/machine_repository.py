from sqlalchemy.orm import Session
from app import models, schemas


class MachineRepository:
    def create_machine(self, db: Session, provider_id: int, machine_data: schemas.MachineCreate):
        db_machine = models.Machine(
            provider_id=provider_id,              #legacy: provider_id=machine_data.provider_id,
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

    def get_machine(self, db: Session, machine_id: int) -> models.Machine | None:
        return (
            db.query(models.Machine)
            .filter(models.Machine.id == machine_id)
            .first()
        )

    def list_machines_for_provider(self, db: Session, provider_id: int) -> list[models.Machine]:
        return (
            db.query(models.Machine)
            .filter(models.Machine.provider_id == provider_id)
            .all()
        )

    def provider_owns_machine(self, db: Session, provider_id: int, machine_id: int) -> bool:
        return (
            db.query(models.Machine)
            .filter(
                models.Machine.id == machine_id,
                models.Machine.provider_id == provider_id,
            )
            .count()
            > 0
        )


machine_repository = MachineRepository()