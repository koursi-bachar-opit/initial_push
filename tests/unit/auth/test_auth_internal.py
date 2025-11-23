import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import jwt

from app.auth import auth


def test_parse_mock_token_bad_format(db_session):
    """
    Bad mock token should raise an HTTPException.
    """
    with pytest.raises(HTTPException):
        auth._parse_mock_token_and_create_user(db_session, "badtoken")


def test_parse_mock_token_valid_provider(db_session):
    """
    "provider:email" should create a provider user.
    """
    user = auth._parse_mock_token_and_create_user(
        db_session,
        "provider:alice@example.com",
    )
    assert user.email == "alice@example.com"
    assert user.role.value == "provider"


def test_decode_supabase_jwt_missing_secret(monkeypatch):
    """
    No JWT secret should return 500 from _decode_supabase_jwt().
    """
    monkeypatch.setattr("app.auth.auth.settings.SUPABASE_JWT_SECRET", None)

    with pytest.raises(HTTPException) as exc:
        auth._decode_supabase_jwt("abc.def.ghi")

    assert exc.value.status_code == 500


def test_decode_supabase_jwt_invalid_signature(monkeypatch):
    """
    An invalid JWT signature should return 401.
    """
    monkeypatch.setattr("app.auth.auth.settings.SUPABASE_JWT_SECRET", "TESTSECRET")

    with pytest.raises(HTTPException) as exc:
        auth._decode_supabase_jwt("invalid.jwt.token")

    assert exc.value.status_code == 401


def test_decode_supabase_jwt_valid(monkeypatch):
    """
    A JWT should be decoded successfully.
    """
    secret = "TESTSECRET"
    monkeypatch.setattr("app.auth.auth.settings.SUPABASE_JWT_SECRET", secret)

    payload = {
        "sub": "123",
        "email": "user@example.com",
        "user_metadata": {"role": "provider"},
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }

    token = jwt.encode(payload, secret, algorithm="HS256")
    decoded = auth._decode_supabase_jwt(token)

    assert decoded["sub"] == "123"
    assert decoded["email"] == "user@example.com"