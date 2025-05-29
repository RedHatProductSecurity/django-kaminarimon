from pathlib import Path

from django.core.management.utils import get_random_secret_key

DEBUG = True
SECRET_KEY = get_random_secret_key()  # pragma: allowlist secret

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "kaminarimon",
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

AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1:6969"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
