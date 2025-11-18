from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.auth import get_current_user
from app.repositories.machine_repository import machine_repository

router = APIRouter()


@router.get("/{machine_id}", response_model=schemas.MachineRead)
def get_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    machine = machine_repository.get_machine(db, machine_id)

    if not machine:
        raise HTTPException(404, "Machine not found")

    # Providers can only see their own machines
    if user.role == models.UserRole.PROVIDER and machine.provider_id != user.id:
        raise HTTPException(403, "Not allowed")

    return machine


@router.get("/", response_model=list[schemas.MachineRead])
def list_machines(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if user.role != models.UserRole.PROVIDER:
        raise HTTPException(403, "Only providers can view machines")

    return machine_repository.list_machines_for_provider(db, user.id)


@router.delete("/{machine_id}", status_code=204)
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    machine = machine_repository.get_machine(db, machine_id)

    if not machine:
        raise HTTPException(404, "Machine not found")

    if machine.provider_id != user.id:
        raise HTTPException(403, "Not allowed")

    db.delete(machine)
    db.commit()


@router.post("/", response_model=schemas.MachineRead, status_code=201)
def create_machine(
    payload: schemas.MachineCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if user.role != models.UserRole.PROVIDER:
        raise HTTPException(403, "Only providers can create machines")

    return machine_repository.create_machine(db, user.id, payload)