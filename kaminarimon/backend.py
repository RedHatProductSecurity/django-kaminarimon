import json
import os

import ldap
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from ldap.filter import escape_filter_chars
from rest_framework.exceptions import AuthenticationFailed


LDAP_DEFAULT_BASE_DN = "dc=ipa,dc=redhat,dc=com"

def _ldap_connect():
    servers = getattr(settings, "KAMINARIMON_LDAP_SERVERS", None)
    if not servers:
        raise ImproperlyConfigured(
            "KAMINARIMON_LDAP_SERVERS must be set in Django settings"
        )

    conn = ldap.initialize(" ".join(servers), bytes_mode=False)
    conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)

    timeout = getattr(settings, "KAMINARIMON_LDAP_TIMEOUT", 10)
    conn.set_option(ldap.OPT_NETWORK_TIMEOUT, timeout)
    conn.set_option(ldap.OPT_TIMEOUT, timeout)

    bind_dn = getattr(settings, "KAMINARIMON_LDAP_BIND_DN", None)
    if bind_dn:
        # Simple bind for test/dev environments without Kerberos
        bind_password = getattr(settings, "KAMINARIMON_LDAP_BIND_PASSWORD", "")
        if not bind_password:
            raise ImproperlyConfigured(
                "KAMINARIMON_LDAP_BIND_PASSWORD must be set when using "
                "KAMINARIMON_LDAP_BIND_DN (empty password results in "
                "anonymous bind)"
            )
        conn.simple_bind_s(bind_dn, bind_password)
    else:
        conn.sasl_gssapi_bind_s()

    return conn

# Global TODO: Move hardcoded data into settings
def get_ldap_groups(user_dn, conn):
    base_dn = getattr(settings, "KAMINARIMON_LDAP_BASE_DN", LDAP_DEFAULT_BASE_DN)
    group_base = f"cn=groups,cn=accounts,{base_dn}"
    groups = conn.search_s(
        group_base,
        ldap.SCOPE_SUBTREE,
        f"(member={escape_filter_chars(user_dn)})",
        ["cn"],
    )
    return {group[1]["cn"][0].decode() for group in groups}


def get_user_info(username, conn):
    base_dn = getattr(settings, "KAMINARIMON_LDAP_BASE_DN", LDAP_DEFAULT_BASE_DN)
    user_base = f"cn=users,cn=accounts,{base_dn}"
    attrlist = ["givenName", "sn", "mail"]
    user = conn.search_s(
        user_base,
        ldap.SCOPE_SUBTREE,
        f"(uid={escape_filter_chars(username)})",
        attrlist
    )
    if not user:
        # TODO: log mismatched username
        raise AuthenticationFailed(
            "Could not find matching LDAP account for Kerberos principal"
        )
    return user[0]


class LDAPRemoteUser(ModelBackend):
    # This emulates django's RemoteUserBackend but with some modifications
    # to the authenticate method in order to always synchronize DB users
    # with the remote system (LDAP)
    # TODO: in Django 4.1, the override to authenticate is not necessary
    # as configure_user has been changed to do both initial configuration
    # and continuous synchronization:
    # https://github.com/django/django/pull/15492

    def authenticate(self, request, krb_principal):
        """
        The username passed as ``krb_principal`` is considered trusted.

        This method returns the ``User`` object linked to the given username,
        either by fetching it from the database if it exists or by creating
        a new one. In both cases, the ``User`` object is synchronized with
        the configured LDAP server for authorization purposes.
        """
        if not krb_principal:
            return
        User = get_user_model()
        username = self.clean_username(krb_principal)

        user, created = User._default_manager.get_or_create(
            **{User.USERNAME_FIELD: username},
        )
        if created:
            user = self.configure_user(request, user)
        user = self.sync_user(request, user)
        return user if self.user_can_authenticate(user) else None

    def configure_user(self, request, user):
        """
        Configure a user after creation and return the updated user.
        """
        user.set_unusable_password()
        return user

    def sync_user(self, request, user):
        """
        Synchronize the user with the external system and return the updated user.
        """
        username = user.get_username()

        conn = _ldap_connect()
        try:
            dn, attrs = get_user_info(username, conn)
            groups = get_ldap_groups(dn, conn)
        finally:
            conn.unbind_s()

        # Note: we simply create Groups without handling Django-style permissions
        # since we don't really use them -- we use PostgreSQL RLS
        group_objs = [Group.objects.get_or_create(name=group)[0] for group in groups]
        user.first_name = attrs["givenName"][0].decode()
        user.last_name = attrs["sn"][0].decode()
        user.email = attrs["mail"][0].decode()
        user.is_active = bool(set(settings.PUBLIC_READ_GROUPS) & groups)
        user.is_staff = settings.SERVICE_MANAGE_GROUP in groups
        user.is_superuser = settings.SERVICE_MANAGE_GROUP in groups
        # Note: unlike django-auth-ldap, we do create users for anyone who
        # attempts to connect to the service, however if they do not have the
        # required group for is_active (e.g. red-hat-product-security)
        # the user will be denied access when performing the user_can_authenticate
        # check
        user.save()
        user.groups.set(group_objs)
        return user

    def clean_username(self, username):
        """
        Perform any cleaning on the "username" prior to using it to get or
        create the ``User`` object. Return the cleaned username.
        """
        KRB5_TO_LDAP_MAP = json.loads(os.getenv("KRB5_TO_LDAP_MAP", "{}"))
        # username is a kerberos principal, extract the relevant part
        if username in KRB5_TO_LDAP_MAP:
            return KRB5_TO_LDAP_MAP[username]
        return username.rsplit("@", 1)[0]
