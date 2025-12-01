from fastapi import APIRouter, Depends
from uuid import UUID

from app.auth.public import ensure_provider
from .service import BenchmarkService, get_benchmark_service
from .schemas import BenchmarkCreate, BenchmarkRead

router = APIRouter()

#Provider upload
@router.post("/machines/{machine_id}", response_model=BenchmarkRead)
def upload_machine_benchmark(
    machine_id: UUID,
    payload: BenchmarkCreate,
    user=Depends(ensure_provider),  #ensures provider role
    service: BenchmarkService = Depends(get_benchmark_service),
):
    return service.create_benchmark(
        machine_id=machine_id,
        provider_user_id=user.id,
        payload=payload,
    )

#Public read
@router.get("/machines/{machine_id}", response_model=list[BenchmarkRead])
def get_machine_benchmarks(
    machine_id: UUID,
    service: BenchmarkService = Depends(get_benchmark_service),
):
    return service.list_machine_benchmarks(machine_id)

@router.get("/listings/{listing_id}", response_model=list[BenchmarkRead])
def get_listing_benchmarks(
    listing_id: UUID,
    service: BenchmarkService = Depends(get_benchmark_service),
):
    return service.list_listing_benchmarks(listing_id)