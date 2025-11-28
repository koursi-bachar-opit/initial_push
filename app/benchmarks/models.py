import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class MachineBenchmark(Base):
    __tablename__ = "machine_benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=True)

    name = Column(String, nullable=False)
    score = Column(String, nullable=False)

    methodology_uri = Column(String, nullable=True)
    artifact_uri = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())