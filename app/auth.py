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
    Fetch user from DB or create one.
    Now: Applies role from Supabase metadata on first creation.
    """
    user = db.query(models.User).filter_by(supabase_id=sub).first()

    if user:
        return user

    # Map Supabase role string → Enum
    if role:
        role_enum = models.UserRole(role.upper())
    else:
        role_enum = models.UserRole.BUYER  # default

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


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # If no token, dev mode
    if not creds:
        if os.getenv("DEV_MODE") == "true":
            return models.User(
                id=0,
                supabase_id="dev-user",
                email="dev@example.com",
                role=models.UserRole.PROVIDER,
            )
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = creds.credentials

    # CI MOCK MODE: handle "provider:alice"
    if ":" in token and not token.count(".") == 2:
        # Format: role:email
        try:
            role_str, email = token.split(":")
            role_enum = models.UserRole(role_str.upper())
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid mock token")

        # Return a fake user WITHOUT touching DB
        return models.User(
            id=999,  # CI test user
            supabase_id=f"mock-{email}",
            email=email,
            role=role_enum,
        )

    # REAL JWT: decode Supabase token
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