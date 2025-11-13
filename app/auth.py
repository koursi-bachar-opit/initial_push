import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from app.config import settings

# HTTPBearer allows token-based auth (Authorization: Bearer <token>)
security = HTTPBearer(auto_error=False)

def _parse_mock_token(token: str):
    """
    Parse a mock token in the format 'role:username'.
    Used for local/testing environments when no Supabase JWT is configured.
    """
    try:
        role, username = token.split(":", 1)
        role = role.strip().lower()
        if role not in {"buyer", "provider", "admin", "org_admin"}:
            raise ValueError
        return {"role": role, "username": username.strip()}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid mock token format")

def _decode_jwt_token(token: str):
    """
    Decode and verify a real JWT using the Supabase public key (RS256).
    Falls back to a safe failure mode if verification fails.
    """
    try:
        decoded = jwt.decode(
            token,
            settings.SUPABASE_JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return {
            "role": decoded.get("role", "buyer"),
            "username": decoded.get("email") or decoded.get("sub"),
        }
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT")

def get_current_identity(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Main dependency used by all protected endpoints.
    Automatically selects between:
    - Real JWT validation (if Supabase key set)
    - Mock parsing for local/testing environments
    """
    if not creds:
        return {"role": "provider", "username": "demo_user"} #Later (when connecting Supabase) revert to: raise HTTPException(status_code=401, detail="Missing bearer token")

    token = creds.credentials
    if settings.SUPABASE_JWT_PUBLIC_KEY:
        return _decode_jwt_token(token)
    return _parse_mock_token(token)

def require_roles(*allowed_roles):
    """
    Factory dependency generator.
    Restricts endpoint access to users whose 'role' is in allowed_roles.
    """
    def dependency(identity=Depends(get_current_identity)):
        if identity["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return identity
    return dependency