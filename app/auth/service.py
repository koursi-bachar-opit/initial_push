from typing import Optional

import jwt
from jwt import PyJWTError
from fastapi import Depends
from sqlalchemy.orm import Session

from app.users import user_repository
from app.users.models import User
from app.config import settings
from app.database import get_db


class AuthService:
    """
    Bridges Supabase authentication with the internal User domain.
    Handles decoding tokens, parsing mock tokens, and provisioning users.
    """

    def __init__(self, db: Session):
        self.db = db
        self.supabase_jwt_secret = settings.SUPABASE_JWT_SECRET

    # ---- Internal helpers -------------------------------------------------

    def _decode_supabase_jwt(self, token: str) -> dict:
        """
        Decode the JWT we get from Supabase. Mirrors the old behavior:
        - Uses HS256 with SUPABASE_JWT_SECRET
        - Does NOT verify 'aud'
        """
        if not self.supabase_jwt_secret:
            raise RuntimeError("SUPABASE_JWT_SECRET not set.")

        try:
            return jwt.decode(
                token,
                self.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except PyJWTError as e:
            # We raise ValueError so the caller can turn this into a 401
            raise ValueError(f"Invalid or expired JWT: {str(e)}")

    def _get_or_create_user(
        self, sub: str, email: Optional[str], role: Optional[str]
    ) -> User:
        """
        Centralized "provision or fetch" logic, matching the old _get_or_create_user.
        """
        return user_repository.get_or_create_user_by_supabase_id(
            db=self.db,
            sub=sub,
            email=email,
            role=role,
        )

    # ---- Public API -------------------------------------------------------

    def get_current_user(self, token: Optional[str]) -> Optional[User]:
        """
        Returns the authenticated user OR None (if no token).

        Supported formats:

        1. Mock tokens for tests/local dev:
           - "provider:alice@example.com"
           - "admin:admin@example.com"
           - "buyer:buyer@example.com"

           These are NOT JWTs; we parse "role:email" and provision a user.

        2. Real Supabase JWTs:
           - HS256-signed, with 'sub', 'email' (or user_metadata.email),
             and optional user_metadata.role.
        """
        if not token:
            return None

        token = token.strip()

        # Strip any "Bearer " prefix if it leaked through here
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        # ---- 1) Mock token: "role:email" ---------------------------------
        # This matches what the tests are sending via auth_headers_for/auth_headers_by_role
        # e.g. "provider:provider@example.com"
        if ":" in token:
            role_str, email = token.split(":", 1)
            role_str = role_str.lower()

            # Use email as both sub and email, same as the original implementation
            return self._get_or_create_user(
                sub=email,
                email=email,
                role=role_str,
            )

        # ---- 2) Real Supabase JWT -----------------------------------------
        payload = self._decode_supabase_jwt(token)

        sub = payload.get("sub")
        # Supabase sometimes nests email in user_metadata
        email = payload.get("email") or payload.get("user_metadata", {}).get("email")
        metadata = payload.get("user_metadata") or {}
        role = metadata.get("role")

        if not sub or not email:
            raise ValueError("Invalid JWT payload: missing 'sub' or 'email'.")

        return self._get_or_create_user(sub=sub, email=email, role=role)


# DI helper for FastAPI
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)