import os
from fastapi import Depends, HTTPException, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from jwt import InvalidTokenError

from app.config import settings
from app.database import get_db
from app import models
from app.repositories import user_repository

security = HTTPBearer(auto_error=False)


def _get_or_create_user(db: Session, sub: str, email: str, role: str | None) -> models.User:
    """Get user from user_repository"""
    """Load or create from JWT ident"""
    return user_repository.get_or_create_user_by_supabase_id(
        db=db,
        sub=sub,
        email=email,
        role=role,
    )


def _decode_supabase_jwt(token: str) -> dict:
    """
    Decode the JWT we get from Supabase. This uses the shared HS256 secret from Supabase.
    If someone gives us an invalid or expired token, fail fast with a 401.
    """
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


def _parse_mock_token_and_create_user(db: Session, token: str) -> models.User:
    """
    When running locally without Supabase, allow tokens like provider:alice@example.com. 
    This allows impersonating a user quickly without going through OAuth.
    """
    if ":" not in token:
        raise HTTPException(status_code=401, detail="Invalid mock token")

    role_str, email = token.split(":", 1)

    #Auto-create or fetch a DB user
    user = user_repository.get_or_create_user_by_supabase_id(
        db=db,
        sub = email,
        email=email,
        role=role_str.lower(),
    )

    return user


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    """
    1. Check the Bearer header (Supabase uses it)
    2. If no header, use cookie.
    3. If token has "role:email" format, consider as mock local creds
    4. Otherwise, decode the real JWT
    """
    token = None

    #Request ordering
    #1: Bearer header
    if creds:
        token = creds.credentials.strip()

    #2: Cookie
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    #3: Mock token
    if ":" in token:
        return _parse_mock_token_and_create_user(db, token)

    #Must look like a JWT
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
    """Use this dependency to protect routes so only certain roles can reach them."""
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
    Returns a user if a valid token is provided.
    Returns a None type if it's not authenticated.
    """
    token = None

    if creds:
        token = creds.credentials.strip()
    elif access_token:
        token = access_token
    else:
        return None

    #Mock token
    if ":" in token:
        return _parse_mock_token_and_create_user(db, token)

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