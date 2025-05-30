from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from kaminarimon.views import _handle_jwt_auth


@api_view()
def obtain_token_pair_view(request: Request) -> Response:
    return _handle_jwt_auth(request)
