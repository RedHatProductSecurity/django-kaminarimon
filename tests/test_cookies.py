import pytest
from rest_framework import status

pytestmark = pytest.mark.unit


def test_cookies(client, admin_user, live_server, basic_auth_header):
    # set cookie
    r = client.get("/auth/token", HTTP_AUTHORIZATION=basic_auth_header)

    assert r.status_code == status.HTTP_200_OK

    cookie = r.cookies.get("kaminarimon_refresh")
    assert cookie is not None

    assert cookie["secure"]
    assert cookie["httponly"]
    assert cookie["samesite"] == "Strict"

    r = client.get("/auth/token/refresh")
    assert r.status_code == status.HTTP_200_OK
    assert r.json().get("access")


def test_explicit_refresh(client, admin_user, live_server, basic_auth_header):
    r = client.get("/auth/token", HTTP_AUTHORIZATION=basic_auth_header)
    assert r.status_code == status.HTTP_200_OK
    refresh = r.json()["refresh"]

    # delete cookie
    del client.cookies["kaminarimon_refresh"]

    # explicit refresh token
    r = client.post("/auth/token/refresh", data={"refresh": refresh})
    assert r.status_code == status.HTTP_200_OK
    assert r.json().get("access")
