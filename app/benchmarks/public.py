from typing import List
from uuid import UUID
from typing_extensions import Protocol
from fastapi import Depends
from .service import BenchmarkService, get_benchmark_service
from .schemas import BenchmarkRead, BenchmarkCreate

class BenchmarksPublic(Protocol):
    def get_benchmarks_for_machine(self, machine_id: UUID) -> List[BenchmarkRead]: ...
    def get_benchmarks_for_listing(self, listing_id: UUID) -> List[BenchmarkRead]: ...
    def create_benchmark(self, machine_id: UUID, payload: BenchmarkCreate) -> BenchmarkRead:...

class BenchmarksPublicImpl(BenchmarksPublic):
    def __init__(self, service: BenchmarkService):
        self.service = service

    def create_benchmark(self, machine_id: UUID, payload: BenchmarkCreate) -> BenchmarkRead:
        return self.service.create_benchmark(machine_id, payload)

    def get_benchmarks_for_machine(self, machine_id: UUID):
        return self.service.list_machine_benchmarks(machine_id)

    def get_benchmarks_for_listing(self, listing_id: UUID):
        return self.service.list_listing_benchmarks(listing_id)

def get_benchmarks_public(
    service: BenchmarkService = Depends(get_benchmark_service),
):
    return BenchmarksPublicImpl(service)