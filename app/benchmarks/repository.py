from typing import List, Optional
from sqlalchemy.orm import Session
from .models import MachineBenchmark
from .schemas import BenchmarkCreate

class BenchmarkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, machine_id, payload: BenchmarkCreate) -> MachineBenchmark:
        obj = MachineBenchmark(
            machine_id=machine_id,
            listing_id=payload.listing_id,
            name=payload.name,
            score=payload.score,
            methodology_uri=payload.methodology_uri,
            artifact_uri=payload.artifact_uri,
        )

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj


    def list_for_machine(self, machine_id) -> List[MachineBenchmark]:
        return (
            self.db.query(MachineBenchmark)
            .filter(MachineBenchmark.machine_id == machine_id)
            .order_by(MachineBenchmark.created_at.desc())
            .all()
        )

    def list_for_listing(self, listing_id) -> List[MachineBenchmark]:
        return (
            self.db.query(MachineBenchmark)
            .filter(MachineBenchmark.listing_id == listing_id)
            .order_by(MachineBenchmark.created_at.desc())
            .all()
        )