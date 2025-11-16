import pytest
from fastapi import HTTPException

from app import auth

import jwt
from datetime import datetime, timedelta


def test_parse_mock_token_bad_format(db_session):
    with pytest.raises(HTTPException):
        auth._parse_mock_token_and_create_user(db_session, "badtoken")


def test_parse_mock_token_valid_provider(db_session):
    user = auth._parse_mock_token_and_create_user(
        db_session,
        "provider:alice@example.com",
    )
    assert user.email == "alice@example.com"
    assert user.role.value == "provider"


def test_decode_supabase_jwt_missing_secret(monkeypatch):
    #Remove secret
    monkeypatch.setattr("app.auth.settings.SUPABASE_JWT_SECRET", None)

    with pytest.raises(HTTPException) as exc:
        auth._decode_supabase_jwt("abc.def.ghi")

    assert exc.value.status_code == 500


def test_decode_supabase_jwt_invalid_signature(monkeypatch):
    monkeypatch.setattr("app.auth.settings.SUPABASE_JWT_SECRET", "TESTSECRET")

    with pytest.raises(HTTPException) as exc:
        auth._decode_supabase_jwt("invalid.jwt.token")

    assert exc.value.status_code == 401


def test_decode_supabase_jwt_valid(monkeypatch):
    import jwt
    from app import auth
    from datetime import datetime, timedelta, timezone

    secret = "TESTSECRET"
    monkeypatch.setattr("app.auth.settings.SUPABASE_JWT_SECRET", secret)

    payload = {
        "sub": "123",
        "email": "user@example.com",
        "user_metadata": {"role": "provider"},
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    decoded = auth._decode_supabase_jwt(token)
    assert decoded["sub"] == "123"
    assert decoded["email"] == "user@example.com"