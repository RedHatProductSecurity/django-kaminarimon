from django.urls import path

from kaminarimon.views import refresh_token
from tests.cookie_test_app.views import obtain_token_pair_view, test_user_view

urlpatterns = [
    path("auth/token", obtain_token_pair_view, name="token_obtain"),
    path("auth/token/refresh", refresh_token, name="token_refresh"),
    path("test/user", test_user_view, name="test_user"),
]
