import base64

import pytest

from kaminarimon.backend import LDAPRemoteUser


@pytest.fixture
def normal_user():
    return "foo@REDHAT.COM"


@pytest.fixture
def normal_user_ipa():
    return "foo@IPA.REDHAT.COM"


@pytest.fixture
def host_user():
    return "host/myservice.redhat.com@REDHAT.COM"


@pytest.fixture
def hardcoded_user():
    return "host/sdengine-foo.redhat.com@REDHAT.COM"


@pytest.fixture
def backend():
    return LDAPRemoteUser()


@pytest.fixture
def valid_user_username():
    return "testuser"


@pytest.fixture
def valid_service_username():
    return "testservice"


@pytest.fixture
def invalid_service_username():
    return "foo"


@pytest.fixture
def basic_auth_header():
    credentials = "admin:password"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"
