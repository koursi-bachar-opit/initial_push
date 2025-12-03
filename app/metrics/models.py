from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class MetricSample(Base):
    """
    A single time-stamped operational measurement for a machine.
    Append-only: service layer enforces no updates/deletes for historical integrity.
    """
    __tablename__ = "metric_samples"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    #When the metric snapshot was recorded on the machine/agent side
    recorded_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    gpu_util = Column(Float, nullable=True)      #percent (0–100)
    cpu_util = Column(Float, nullable=True)      #percent (0–100)
    mem_used_gb = Column(Float, nullable=True)   #used RAM in GB
    net_rx_mb = Column(Float, nullable=True)     #received MB during window
    net_tx_mb = Column(Float, nullable=True)     #transmitted MB during window

    __table_args__ = (
        #fast time-series queries: "metrics for machine X between t1 and t2"
        Index("ix_metric_samples_machine_time", "machine_id", "recorded_at"),
    )

    def __repr__(self) -> str:  #debugging helper
        return (
            f"<MetricSample id={self.id} machine_id={self.machine_id} "
            f"recorded_at={self.recorded_at}>"
        )