"""
User schemas for the users domain.
"""
# from pydantic import BaseModel, ConfigDict
# from typing import Optional
# from uuid import UUID
# from datetime import datetime
# from enum import Enum


# class UserRole(str, Enum):
#     BUYER = "buyer"
#     PROVIDER = "provider"
#     ADMIN = "admin"
#     ORG_ADMIN = "org_admin"


# class UserRead(BaseModel):
#     id: UUID
#     supabase_id: str
#     email: str
#     role: UserRole
#     created_at: datetime

#     model_config = ConfigDict(from_attributes=True)


# class UserMe(BaseModel):
#     """
#     Returned when the client asks for their authenticated user info.
#     (Commonly used in /auth/me style endpoints.)
#     """
#     id: UUID
#     email: str
#     role: UserRole

#     model_config = ConfigDict(from_attributes=True)