from typing import Callable
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTAuthenticationMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.authenticator = JWTAuthentication()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        def get_user():
            try:
                user_auth_tuple = self.authenticator.authenticate(request)
            except InvalidToken:
                return AnonymousUser()
            if user_auth_tuple is None:
                return AnonymousUser()
            return user_auth_tuple[0]
        request.user = SimpleLazyObject(lambda: get_user())
        return self.get_response(request)
