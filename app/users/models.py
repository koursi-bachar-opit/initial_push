from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
import uuid

from app.database import Base


class UserRole(str, Enum):
    BUYER = "buyer"
    PROVIDER = "provider"
    ADMIN = "admin"
    ORG_ADMIN = "org_admin"


class User(Base):
    """
    Marketplace user.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), nullable=False, default=UserRole.BUYER)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    #A provider can own multiple machines (casecasde delete for data integrity)
    machines = relationship("Machine", back_populates="provider", cascade="all, delete")