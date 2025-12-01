from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from .models import MetricSample


class MetricsRepository:
    """
    Persistence layer for metric samples.
    """
    def __init__(self, db: Session):
        self.db = db

    #Create
    def create_sample(
        self,
        machine_id: UUID,
        recorded_at: datetime,
        gpu_util: Optional[float],
        cpu_util: Optional[float],
        mem_used_gb: Optional[float],
        net_rx_mb: Optional[float],
        net_tx_mb: Optional[float],
    ) -> MetricSample:
        sample = MetricSample(
            machine_id=machine_id,
            recorded_at=recorded_at,
            gpu_util=gpu_util,
            cpu_util=cpu_util,
            mem_used_gb=mem_used_gb,
            net_rx_mb=net_rx_mb,
            net_tx_mb=net_tx_mb,
        )
        self.db.add(sample)
        self.db.commit()
        self.db.refresh(sample)
        return sample

    #Fetch list
    def list_samples(
        self,
        machine_id: UUID,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[MetricSample]:
        stmt = (
            select(MetricSample)
            .where(MetricSample.machine_id == machine_id)
            .order_by(MetricSample.recorded_at)
        )

        if start:
            stmt = stmt.where(MetricSample.recorded_at >= start)
        if end:
            stmt = stmt.where(MetricSample.recorded_at <= end)
        if limit:
            stmt = stmt.limit(limit)

        return list(self.db.scalars(stmt).all())

    #Latest sample
    def get_latest_sample(self, machine_id: UUID) -> Optional[MetricSample]:
        stmt = (
            select(MetricSample)
            .where(MetricSample.machine_id == machine_id)
            .order_by(desc(MetricSample.recorded_at))
            .limit(1)
        )
        return self.db.scalars(stmt).first()