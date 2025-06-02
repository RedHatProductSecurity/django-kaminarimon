import pytest
from rest_framework import status

pytestmark = pytest.mark.unit


def test_cookies(admin_client, live_server):
    # set cookie
    r = admin_client.get("/auth/token")

    assert r.status_code == status.HTTP_200_OK

    cookie = r.cookies.get("kaminarimon_refresh")
    assert cookie is not None

    assert cookie["secure"]
    assert cookie["httponly"]
    assert cookie["samesite"] == "Strict"

    r = admin_client.get("/auth/token/refresh")
    assert r.status_code == status.HTTP_200_OK
    assert r.json().get("access")


def test_explicit_refresh(admin_client, live_server):
    r = admin_client.get("/auth/token")
    assert r.status_code == status.HTTP_200_OK
    refresh = r.json()["refresh"]

    # delete cookie
    del admin_client.cookies["kaminarimon_refresh"]

    # explicit refresh token
    r = admin_client.post("/auth/token/refresh", data={"refresh": refresh})
    assert r.status_code == status.HTTP_200_OK
    assert r.json().get("access")
