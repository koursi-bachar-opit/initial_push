from sqlalchemy import func, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class AccessCredential(Base):
    __tablename__ = "access_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        )

    #Access creds
    vpn_config_uri = Column(String, nullable=True)
    ssh_public_key_fingerprint = Column(String, nullable=True)

    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    #Relationship back to booking
    booking = relationship("Booking", back_populates="access_credentials")