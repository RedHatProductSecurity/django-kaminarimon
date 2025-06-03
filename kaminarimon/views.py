from datetime import datetime, timedelta, timezone

from django.conf import settings
from drf_spectacular.utils import (OpenApiRequest, OpenApiResponse,
                                   extend_schema, extend_schema_view)
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .auth import KerberosAuthentication


def _handle_jwt_auth(request: Request) -> Response:
    refresh_token = RefreshToken.for_user(request.user)
    data = {
        "refresh": str(refresh_token),
        "access": str(refresh_token.access_token),
    }
    headers = {
        "WWW-Authenticate": f"Negotiate {request.auth}",
    }
    r = Response(data, status=status.HTTP_200_OK, headers=headers)
    # Set a cookie containing the refresh token for browser-based apps
    r.set_cookie(
        key="kaminarimon_refresh",
        value=str(refresh_token),
        expires=datetime.now(tz=timezone.utc) + timedelta(days=1),
        path=getattr(settings, "REFRESH_COOKIE_PATH", "/auth/token/refresh"),
        secure=True,
        httponly=True,
        samesite="Strict",
    )
    return r


@extend_schema_view(
    get=extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                },
            }
        }
    )
)
@api_view()
@authentication_classes((KerberosAuthentication,))
@permission_classes((IsAuthenticated,))
def krb5_obtain_token_pair_view(request: Request) -> Response:
    """
    Takes a kerberos ticket and returns an access and refresh JWT pair.
    """
    return _handle_jwt_auth(request)


@extend_schema_view(
    get=extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                },
            }
        }
    ),
    post=extend_schema(
        description="Takes a refresh type JSON web token and returns an access type JSON web token if the refresh token is valid.",
        request=OpenApiRequest(request=TokenRefreshSerializer),
        responses={"200": OpenApiResponse(response=TokenRefreshSerializer)},
    ),
)
@api_view(["GET", "POST"])
@authentication_classes(())
@permission_classes(())
def refresh_token(request: Request) -> Response:
    if request.method == "GET":
        data = {"refresh": request.COOKIES.get("kaminarimon_refresh")}
    else:
        data = request.data

    serializer = TokenRefreshSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
    except TokenError as e:
        raise InvalidToken(e.args[0])
    return Response(serializer.validated_data, status=status.HTTP_200_OK)
