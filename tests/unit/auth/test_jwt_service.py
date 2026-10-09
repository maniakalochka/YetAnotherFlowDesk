from datetime import UTC, datetime, timedelta

import jwt
import pytest

from flowdesk.modules.auth.service import JWTService

TEST_JWT_SECRET = "test-secret-with-at-least-thirty-two-bytes"  # noqa: S105


def test_jwt_service_creates_decodable_expiring_token() -> None:
    service = JWTService(
        secret_key=TEST_JWT_SECRET,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    token = service.create_access_token("0a02e5de-c18a-462b-9101-8f997b229f51")

    payload = service.decode_access_token(token)

    assert payload["sub"] == "0a02e5de-c18a-462b-9101-8f997b229f51"
    assert "iat" in payload
    assert "exp" in payload


def test_jwt_service_rejects_token_without_expiration() -> None:
    service = JWTService(
        secret_key=TEST_JWT_SECRET,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    token = jwt.encode(
        {"sub": "0a02e5de-c18a-462b-9101-8f997b229f51"},
        TEST_JWT_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.MissingRequiredClaimError):
        service.decode_access_token(token)


def test_jwt_service_rejects_expired_token() -> None:
    service = JWTService(
        secret_key=TEST_JWT_SECRET,
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    token = jwt.encode(
        {
            "sub": "0a02e5de-c18a-462b-9101-8f997b229f51",
            "exp": datetime.now(UTC) - timedelta(seconds=1),
        },
        TEST_JWT_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        service.decode_access_token(token)
