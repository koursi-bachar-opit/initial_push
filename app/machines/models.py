from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class Machine(Base):
    """
    These are the physical servers offered by providers.
    Most hardware attributes are nullable until full buildout.
    """
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)

    #Link to the provider's user account
    provider_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    #Hardware and descriptive attributes (note: to be non nullable later)
    hostname = Column(String, nullable=True)
    location_region = Column(String, nullable=True)

    gpu_model = Column(String, nullable=True)
    gpu_count = Column(Integer, nullable=True)
    vram_gb = Column(Integer, nullable=True)

    cpu_model = Column(String, nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    ram_gb = Column(Integer, nullable=True)

    storage_gb = Column(Integer, nullable=True)
    network_mbps = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    provider = relationship("User", back_populates="machines")
    listings = relationship("Listing", back_populates="machine")