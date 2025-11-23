from sqlalchemy.orm import Session

from .repository import machine_repository
from .schemas import MachineCreate
from .models import Machine

from fastapi import Depends
from app.database import get_db

# class MachineNotFoundError(Exception):
#     pass


# class NotProviderMachineError(Exception):
#     pass


class MachinesService:
    """
    Service layer for machine CRUD and domain rules
    (authorization stays in routes).
    """

    def __init__(self, db: Session):
        self.db = db


    def get_machine(self, machine_id: int) -> Machine:
        machine = machine_repository.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError()  #MachineNotFoundError()
        return machine

    def list_machines_for_provider(self, provider_id: int) -> list[Machine]:
        return machine_repository.list_machines_for_provider(self.db, provider_id)


    def create_machine(self, payload: MachineCreate) -> Machine:
        return machine_repository.create_machine(self.db, payload)


    def delete_machine(self, machine_id: int, provider_id: int):
        machine = machine_repository.get_machine(self.db, machine_id)
        if not machine:
            raise ValueError()  #MachineNotFoundError()

        # Business rule: providers can only delete their own machines
        if machine.provider_id != provider_id:
            raise ValueError()  #NotProviderMachineError()

        self.db.delete(machine)
        self.db.commit()


def get_machines_service(db: Session = Depends(get_db)) -> MachinesService:
    return MachinesService(db)