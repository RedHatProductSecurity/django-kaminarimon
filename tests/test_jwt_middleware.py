import logging

import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.unit


def test_jwt_middleware_with_authenticated_user(client, admin_user, caplog):
    """
    Test that the JWT middleware correctly sets request.user to the authenticated user
    when a valid JWT token is provided.
    """
    refresh_token = RefreshToken.for_user(admin_user)
    access_token = str(refresh_token.access_token)

    with caplog.at_level(logging.INFO, logger="tests.cookie_test_app.middleware"):
        response = client.get(
            "/test/user",
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    assert response.status_code == status.HTTP_200_OK

    # Verify that the log was emitted with the correct user
    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    assert log_record.levelname == "INFO"
    assert "/test/user" in log_record.message
    assert str(admin_user) in log_record.message or admin_user.username in log_record.message


def test_jwt_middleware_without_token(client, caplog):
    with caplog.at_level(logging.INFO, logger="tests.cookie_test_app.middleware"):
        response = client.get("/test/user")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_middleware_with_invalid_token(client, caplog):
    with caplog.at_level(logging.INFO, logger="tests.cookie_test_app.middleware"):
        response = client.get(
            "/test/user",
            HTTP_AUTHORIZATION="Bearer invalid_token_12345"
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_middleware_jwt_auth_requires_jwt_token_not_basic_auth(client, admin_user, basic_auth_header, caplog):
    with caplog.at_level(logging.INFO, logger="tests.cookie_test_app.middleware"):
        response = client.get(
            "/test/user",
            HTTP_AUTHORIZATION=basic_auth_header
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
