from pathlib import Path

from django.core.management.utils import get_random_secret_key

DEBUG = True
SECRET_KEY = get_random_secret_key()  # pragma: allowlist secret

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "tests.cookie_test_app.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "kaminarimon",
    "tests.cookie_test_app",
    "rest_framework_simplejwt",
    "rest_framework",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "kaminarimon.backend.LDAPRemoteUser",
]

DATABASES = {
    "default": {
        "NAME": "test",
        "USER": "test_user",
        "PASSWORD": "test_pass",
        "ENGINE": "django.db.backends.sqlite3",
        "CONN_MAX_AGE": 120,
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

KAMINARIMON_LDAP_SERVERS = ["ldap://127.0.0.1:6969"]
KAMINARIMON_LDAP_BIND_DN = "cn=admin,dc=ipa,dc=redhat,dc=com"
KAMINARIMON_LDAP_BIND_PASSWORD = "adminpassword"
KAMINARIMON_LDAP_BASE_DN = "dc=ipa,dc=redhat,dc=com"
PUBLIC_READ_GROUPS = ["testgroup"]
SERVICE_MANAGE_GROUP = "testgroup"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
