import pytest
from rest_framework.exceptions import AuthenticationFailed

from kaminarimon.backend import get_user_info, get_ldap_groups

pytestmark = pytest.mark.unit


class TestCleanUsername:
    def test_normal_user(self, backend, normal_user):
        assert backend.clean_username(normal_user) == "foo"

    def test_normal_user_ipa(self, backend, normal_user_ipa):
        assert backend.clean_username(normal_user_ipa) == "foo"

    def test_host_user(self, backend, host_user):
        assert backend.clean_username(host_user) == "host/myservice.redhat.com"

    def test_hardcoded_user(self, monkeypatch, backend, hardcoded_user):
        import os

        def mock_getenv(env_var, default=""):
            if env_var == "KRB5_TO_LDAP_MAP":
                return '{"%s": "sdengine"}' % hardcoded_user
            return default

        monkeypatch.setattr(os, "getenv", mock_getenv)

        assert backend.clean_username(hardcoded_user) == "sdengine"


class TestLDAPCommunication:
    def test_user_info_valid_user(self, ldap_conn, valid_user_username):
        dn, attrs = get_user_info(valid_user_username, ldap_conn)
        assert dn == f"uid={valid_user_username},cn=users,cn=accounts,dc=ipa,dc=redhat,dc=com"
        assert attrs["sn"][0].decode() == "Perlis"

    def test_user_info_valid_service(self, ldap_conn, valid_service_username):
        dn, attrs = get_user_info(valid_service_username, ldap_conn)
        assert dn == f"uid={valid_service_username},cn=users,cn=accounts,dc=ipa,dc=redhat,dc=com"
        assert attrs["sn"][0].decode() == "Faker"

    def test_user_info_invalid_service(self, ldap_conn, invalid_service_username):
        with pytest.raises(AuthenticationFailed) as e:
            get_user_info(invalid_service_username, ldap_conn)
        msg = "Could not find matching LDAP account for Kerberos principal"
        assert msg == str(e.value)

    def test_ldap_groups(self, ldap_conn, valid_user_username):
        dn, _ = get_user_info(valid_user_username, ldap_conn)
        groups = get_ldap_groups(dn, ldap_conn)
        assert "testgroup" in groups
