from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.service import AuthService, get_auth_service

security = HTTPBearer(auto_error=False)

#DELETE
#########################################################
from sqlalchemy.orm import Session
def _parse_mock_token_and_create_user(db: Session, token: str):
    """
    Compatibility layer for tests expecting this function in auth.py.
    Delegates to AuthService logic.
    """
    if ":" not in token:
        raise HTTPException(status_code=401, detail="Invalid mock token")

    role_str, email = token.split(":", 1)
    auth_service = AuthService(db)

    return auth_service._get_or_create_user(
        sub=email,
        email=email,
        role=role_str.lower(),
    )


def _decode_supabase_jwt(token: str):
    """
    Compatibility layer for tests expecting this function in auth.py.
    Delegates to AuthService._decode_supabase_jwt and wraps errors in HTTPException.
    """
    try:
        temp = AuthService(db=None)
        return temp._decode_supabase_jwt(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
##########################################################

def require_roles(*roles):
    """
    Enforces that the authenticated user must have one of the specified roles.
    """
    def dependency(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user

    return dependency


def extract_token(credentials: HTTPAuthorizationCredentials, request: Request) -> str | None:
    """
    Extracts a token from Authorization header OR from cookies.
    Header takes priority.
    """
    # First try Authorization header
    if credentials and credentials.credentials:
        return credentials.credentials

    # Fallback: cookie-based auth
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    return None


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    token = extract_token(credentials, request)

    try:
        user = auth_service.get_current_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")

    return user


def optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    token = extract_token(credentials, request)

    try:
        return auth_service.get_current_user(token)
    except Exception:
        return None


# import os
# from fastapi import Depends, HTTPException, Cookie
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# import jwt
# from jwt import InvalidTokenError

# from app.config import settings
# from app.database import get_db
# from app.users.models import User, UserRole
# from app.users import user_repository

# security = HTTPBearer(auto_error=False)


# def _get_or_create_user(db: Session, sub: str, email: str, role: str | None) -> User:
#     """Get user from user_repository"""
#     """Load or create from JWT ident"""
#     return user_repository.get_or_create_user_by_supabase_id(
#         db=db,
#         sub=sub,
#         email=email,
#         role=role,
#     )


# def _decode_supabase_jwt(token: str) -> dict:
#     """
#     Decode the JWT we get from Supabase. This uses the shared HS256 secret from Supabase.
#     If someone gives us an invalid or expired token, fail fast with a 401.
#     """
#     secret = settings.SUPABASE_JWT_SECRET
#     if not secret:
#         raise HTTPException(status_code=500, detail="Supabase JWT secret missing")

#     try:
#         return jwt.decode(
#             token,
#             secret,
#             algorithms=["HS256"],
#             options={"verify_aud": False},
#         )
#     except InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid or expired JWT")


# def _parse_mock_token_and_create_user(db: Session, token: str) -> User:
#     """
#     When running locally without Supabase, allow tokens like provider:alice@example.com. 
#     This allows impersonating a user quickly without going through OAuth.
#     """
#     if ":" not in token:
#         raise HTTPException(status_code=401, detail="Invalid mock token")

#     role_str, email = token.split(":", 1)

#     #Auto-create or fetch a DB user
#     user = user_repository.get_or_create_user_by_supabase_id(
#         db=db,
#         sub = email,
#         email=email,
#         role=role_str.lower(),
#     )

#     return user


# def get_current_user(
#     creds: HTTPAuthorizationCredentials = Depends(security),
#     access_token: str | None = Cookie(default=None),
#     db: Session = Depends(get_db),
# ):
#     """
#     1. Check the Bearer header (Supabase uses it)
#     2. If no header, use cookie.
#     3. If token has "role:email" format, consider as mock local creds
#     4. Otherwise, decode the real JWT
#     """
#     token = None

#     #Request ordering
#     #1: Bearer header
#     if creds:
#         token = creds.credentials.strip()

#     #2: Cookie
#     elif access_token:
#         token = access_token

#     if not token:
#         raise HTTPException(status_code=401, detail="Missing bearer token")

#     #3: Mock token
#     if ":" in token:
#         return _parse_mock_token_and_create_user(db, token)

#     #Must look like a JWT
#     if token.count(".") != 2:
#         raise HTTPException(status_code=401, detail="Invalid bearer token")

#     decoded = _decode_supabase_jwt(token)
#     sub = decoded.get("sub")
#     email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")

#     if not sub or not email:
#         raise HTTPException(status_code=401, detail="Invalid JWT payload")

#     metadata = decoded.get("user_metadata") or {}
#     role = metadata.get("role")

#     return _get_or_create_user(db, sub, email, role)


# def require_roles(*allowed: UserRole):
#     """Use this dependency to protect routes so only certain roles can reach them."""
#     def dep(user: User = Depends(get_current_user)):
#         if user.role not in allowed:
#             raise HTTPException(status_code=403, detail="Forbidden")
#         return user

#     return dep


# def optional_user(
#     creds: HTTPAuthorizationCredentials = Depends(security),
#     access_token: str | None = Cookie(default=None),
#     db: Session = Depends(get_db),
# ):
#     """
#     Returns a user if a valid token is provided.
#     Returns a None type if it's not authenticated.
#     """
#     token = None

#     if creds:
#         token = creds.credentials.strip()
#     elif access_token:
#         token = access_token
#     else:
#         return None

#     #Mock token
#     if ":" in token:
#         return _parse_mock_token_and_create_user(db, token)

#     if token.count(".") != 2:
#         return None

#     decoded = _decode_supabase_jwt(token)
#     sub = decoded.get("sub")
#     email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")

#     if not sub or not email:
#         return None

#     metadata = decoded.get("user_metadata") or {}
#     role = metadata.get("role")

#     return _get_or_create_user(db, sub, email, role)