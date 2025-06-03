from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from kaminarimon.views import _handle_jwt_auth


@api_view()
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAuthenticated,))
def obtain_token_pair_view(request: Request) -> Response:
    return _handle_jwt_auth(request)
