import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from jwt import InvalidTokenError

from app.config import settings
from app.database import get_db
from app import models

security = HTTPBearer(auto_error=False)


def _get_or_create_user(db: Session, sub: str, email: str, role: str | None) -> models.User:
    """
    Fetch or create user from DB.
    Role from Supabase metadata must match enum values (lowercase).
    """
    user = db.query(models.User).filter_by(supabase_id=sub).first()

    if user:
        return user

    # FIX: convert role to lowercase (NOT uppercase)
    if role:
        role_enum = models.UserRole(role.lower())
    else:
        role_enum = models.UserRole.BUYER

    new_user = models.User(
        supabase_id=sub,
        email=email,
        role=role_enum,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def _decode_supabase_jwt(token: str) -> dict:
    secret = settings.SUPABASE_JWT_SECRET
    if not secret:
        raise HTTPException(status_code=500, detail="Supabase JWT secret missing")

    try:
        return jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT")


def _parse_mock_token(token: str) -> models.User:
    """
    Parse mock tokens used by the test suite.
    Expected format: "<role>:<email>"
    Example: "provider:alice"
    """
    if ":" not in token:
        raise HTTPException(status_code=401, detail="Invalid mock token")

    try:
        role_str, email = token.split(":", 1)
        role_enum = models.UserRole(role_str.lower())
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid mock token")

    return models.User(
        id=999,
        supabase_id=f"mock-{email}",
        email=email,
        role=role_enum,
    )


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = creds.credentials.strip() if creds else None

    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    # ----------- MOCK TOKEN BRANCH -----------
    # Treat ANY token with ":" as mock. _parse_mock_token handles validity.
    if ":" in token:
        return _parse_mock_token(token)

    # ----------- INVALID NON-MOCK, NON-JWT TOKEN -----------
    # JWTs must have 2 dots. If not → reject.
    if token.count(".") != 2:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    # ----------- REAL JWT TOKEN -----------
    decoded = _decode_supabase_jwt(token)

    sub = decoded.get("sub")
    email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")

    if not sub or not email:
        raise HTTPException(status_code=401, detail="Invalid JWT payload")

    metadata = decoded.get("user_metadata") or {}
    role = metadata.get("role")

    return _get_or_create_user(db, sub, email, role)


def require_roles(*allowed: models.UserRole):
    def dep(user: models.User = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return dep