from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.service import AuthService, get_auth_service

security = HTTPBearer(auto_error=False)

#marked for deletion
# ----------------------------------------------------------------
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from app.config import settings
def _parse_mock_token_and_create_user(db: Session, token: str):
    """
    Legacy function for tests
    """
    if ":" not in token:
        raise HTTPException(status_code=401, detail="Invalid mock token")

    role_str, email = token.split(":", 1)
    
    from app.users.public import get_users_public
    users_public = get_users_public(db)
    auth_service = AuthService(db=db, users_public=users_public)

    return auth_service._get_or_create_user(
        sub=email,
        email=email,
        role=role_str.lower(),
    )
# def _parse_mock_token_and_create_user(db: Session, token: str):
# 
#     if ":" not in token:
#         raise HTTPException(status_code=401, detail="Invalid mock token")

#     role_str, email = token.split(":", 1)
    
#     # FIX: Use get_auth_service instead of direct instantiation
#     auth_service = get_auth_service(db)  # Changed this line

#     return auth_service._get_or_create_user(
#         sub=email,
#         email=email,
#         role=role_str.lower(),
#     )


def _decode_supabase_jwt(token: str):
    """
    Legacy function for tests.
    Delegates to AuthService._decode_supabase_jwt and wraps errors in HTTPException.
    """
    try:
        class TempAuthService:
            def __init__(self):
                self.supabase_jwt_secret = settings.SUPABASE_JWT_SECRET
            
            def _decode_supabase_jwt(self, token: str) -> dict:
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
                    raise ValueError(f"Invalid or expired JWT: {str(e)}")
        
        temp = TempAuthService()
        return temp._decode_supabase_jwt(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#---------------------------------------------------------------------

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
    Extracts a token from Authorization header or from cookies.
    Header takes priority.
    """
    #Authorization header
    if credentials and credentials.credentials:
        return credentials.credentials

    #cookie-based auth as a second option
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