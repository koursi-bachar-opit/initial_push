from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Listing(Base):
    """
    A listing is something a provider offers for rent.
    For example, a VM, GPU instance, or small compute server.
    Buyers can browse listings and book them for a time window.
    """
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    #The listing links to the underlying machine being rented
    machine_id = Column(
        Integer,
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    #Listing has cardinal relationships to machine and bookings
    machine = relationship("Machine", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")