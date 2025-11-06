import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class TestUserMiddleware:
    """
    Test middleware that accesses request.user and logs it along with the requested path
    for traceability purposes. This verifies that the JWT middleware correctly sets request.user.
    """
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Access request.user to verify it's set correctly by the JWT middleware
        # This should trigger the SimpleLazyObject evaluation
        user = request.user

        # Log the user and requested path for traceability
        user_str = str(user) if user else "None"
        logger.info(f"Request to {request.path} by user: {user_str}")

        return self.get_response(request)

