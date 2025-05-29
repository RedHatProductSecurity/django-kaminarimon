from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .auth import KerberosAuthentication


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
def krb5_obtain_token_pair_view(request):
    """
    Takes a kerberos ticket and returns an access and refresh JWT pair.
    """
    refresh_token = RefreshToken.for_user(request.user)
    data = {
        "refresh": str(refresh_token),
        "access": str(refresh_token.access_token),
    }
    headers = {
        "WWW-Authenticate": f"Negotiate {request.auth}",
    }
    return Response(data, status=status.HTTP_200_OK, headers=headers)
