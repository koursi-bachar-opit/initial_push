from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
from app.auth import require_roles

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.ListingRead,
    status_code=201,
    dependencies=[Depends(require_roles(models.UserRole.PROVIDER, models.UserRole.ADMIN))]
)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    return crud.create_listing(db, listing)


@router.get("/", response_model=list[schemas.ListingRead])
def list_listings(db: Session = Depends(get_db)):
    return crud.get_listings(db)