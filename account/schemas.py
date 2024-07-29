from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import status

from account.serializers.serializers import (
    LoginRequestSerializer,
    WechatLoginRequestSerializer,
    LoginValidateErrorSerializer,
    WechatLoginValidateErrorSerializer,
    LoginResponseSerializer,
    WechatProfilePostSerializer,
)
from utils.schemas import (
    response_schema,
    parameter_ordering,
    parameter_page_size,
    parameter_search,
)
from account.serializers.model import UserSerializer
from utils.serializers import (
    ErrorResponseSerializer,
    ValidationNonFieldErrorSerializer,
)
from wristcheck_api.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE

list_schema_info = dict(
    tags=["user"],
    summary="user_list",
    description="**PERMISSION**: Allows access only to admin users.",
    parameters=[
        parameter_page_size(),
        parameter_ordering(["date_joined", "last_login"], default="-date_joined"),
        parameter_search(["username", "email"]),
    ],
    responses={
        status.HTTP_200_OK: response_schema(
            status.HTTP_200_OK, UserSerializer, many=True
        ),
        status.HTTP_401_UNAUTHORIZED: response_schema(
            status.HTTP_401_UNAUTHORIZED, ErrorResponseSerializer
        ),
        status.HTTP_403_FORBIDDEN: response_schema(
            status.HTTP_403_FORBIDDEN, ErrorResponseSerializer
        ),
    },
)

retrieve_schema_info = dict(
    summary="user_retrieve",
    description="**PERMISSION**: Allows access only to owner or admin users.",
    responses={
        status.HTTP_200_OK: response_schema(
            status.HTTP_200_OK, LoginResponseSerializer, many=False
        ),
        status.HTTP_401_UNAUTHORIZED: response_schema(
            status.HTTP_401_UNAUTHORIZED, ErrorResponseSerializer
        ),
    },
)

login_schema_info = dict(
    tags=["user"],
    summary="user_login",
    description="Login with username and password and return a token.",
    request=LoginRequestSerializer,
    responses={
        status.HTTP_200_OK: response_schema(
            status.HTTP_200_OK, LoginResponseSerializer, many=False
        ),
        status.HTTP_400_BAD_REQUEST: response_schema(
            status.HTTP_400_BAD_REQUEST, LoginValidateErrorSerializer
        ),
        status.HTTP_401_UNAUTHORIZED: response_schema(
            status.HTTP_401_UNAUTHORIZED, ErrorResponseSerializer
        ),
    },
)

wechat_mini_login_schema_info = dict(
    tags=["user"],
    summary="wechat_mini_login",
    description="Login with code and return a token.",
    request=WechatLoginRequestSerializer,
    responses={
        status.HTTP_200_OK: response_schema(
            status.HTTP_200_OK, LoginResponseSerializer, many=False
        ),
        status.HTTP_400_BAD_REQUEST: response_schema(
            status.HTTP_400_BAD_REQUEST, WechatLoginValidateErrorSerializer
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: response_schema(
            status.HTTP_500_INTERNAL_SERVER_ERROR, ErrorResponseSerializer
        ),
    },
)

profile_schema_info = dict(
    tags=["user"],
    summary="user_profile",
    description="**PERMISSION**: Allows access only to authenticated users.",
    responses={
        status.HTTP_200_OK: response_schema(
            status.HTTP_200_OK, UserSerializer, many=False
        ),
        status.HTTP_401_UNAUTHORIZED: response_schema(
            status.HTTP_401_UNAUTHORIZED, ErrorResponseSerializer
        ),
    },
)

wechat_profile_schema_info = dict(
    tags=["user"],
    summary="wechat_profile",
    description="update wechat profile, eg: avatar, nickname <br>"
    "At least one of 'nickname' or 'avatar_url' must be provided.",
    request=WechatProfilePostSerializer,
    responses={
        status.HTTP_200_OK: None,
        status.HTTP_401_UNAUTHORIZED: response_schema(
            status.HTTP_401_UNAUTHORIZED, ErrorResponseSerializer
        ),
        status.HTTP_400_BAD_REQUEST: response_schema(
            status.HTTP_400_BAD_REQUEST, ValidationNonFieldErrorSerializer
        ),
    },
)
