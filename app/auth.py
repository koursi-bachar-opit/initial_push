import os
from fastapi import Depends, HTTPException, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from jwt import InvalidTokenError

from app.config import settings
from app.database import get_db
from app import models

security = HTTPBearer(auto_error=False)

# INTERNAL HELPERS
def _get_or_create_user(db: Session, sub: str, email: str, role: str | None) -> models.User:
    user = db.query(models.User).filter_by(supabase_id=sub).first()

    if user:
        return user

    role_enum = models.UserRole(role.lower()) if role else models.UserRole.BUYER

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
    if ":" not in token:
        raise HTTPException(status_code=401, detail="Invalid mock token")

    role_str, email = token.split(":", 1)
    return models.User(
        id=999,
        supabase_id=f"mock-{email}",
        email=email,
        role=models.UserRole(role_str.lower()),
    )



# AUTH REQUIREMENTS
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    """
    Full authentication required.
    Checks header first, then cookie.
    """
    token = None

    # Priority 1: Bearer header
    if creds:
        token = creds.credentials.strip()

    # Priority 2: HttpOnly cookie
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    # mock token
    if ":" in token:
        return _parse_mock_token(token)

    if token.count(".") != 2:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    decoded = _decode_supabase_jwt(token)
    sub = decoded.get("sub")
    email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")

    if not sub or not email:
        raise HTTPException(status_code=401, detail="Invalid JWT payload")

    metadata = decoded.get("user_metadata") or {}
    role = metadata.get("role")

    return _get_or_create_user(db, sub, email, role)

def require_roles(*allowed: models.UserRole):
    """
    Dependency to enforce role-based access.
    Used in routes such as @router.post(..., dependencies=[Depends(require_roles(...))])
    """
    def dep(user: models.User = Depends(get_current_user)):
        if user.role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return dep


def optional_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    """
    Returns a user if a valid token (header or cookie) is provided.
    Returns None if unauthenticated.
    Perfect for Jinja2 pages.
    """
    token = None

    # Header first
    if creds:
        token = creds.credentials.strip()

    # Cookie second
    elif access_token:
        token = access_token

    else:
        return None

    # mock tokens
    if ":" in token:
        return _parse_mock_token(token)

    if token.count(".") != 2:
        return None

    decoded = _decode_supabase_jwt(token)
    sub = decoded.get("sub")
    email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")

    if not sub or not email:
        return None

    metadata = decoded.get("user_metadata") or {}
    role = metadata.get("role")

    return _get_or_create_user(db, sub, email, role)