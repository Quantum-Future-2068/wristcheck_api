from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from account.serializers.serializers import (
    LoginRequestSerializer,
    WechatLoginRequestSerializer,
    LoginValidateErrorSerializer,
    WechatLoginValidateErrorSerializer,
)
from utils.schemas import (
    response_schema,
    parameter_ordering,
    parameter_page_size,
    parameter_search,
)
from account.serializers.model import UserSerializer
from utils.serializers import ErrorResponseSerializer
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
        200: response_schema(200, UserSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

retrieve_schema_info = dict(
    summary="user_retrieve",
    description="**PERMISSION**: Allows access only to owner or admin users.",
    responses={
        200: response_schema(200, UserSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
    },
)

login_schema_info = dict(
    tags=["user"],
    summary="user_login",
    description="Login with username and password and return a token.",
    request=LoginRequestSerializer,
    responses={
        200: response_schema(200, UserSerializer, many=False),
        400: response_schema(400, LoginValidateErrorSerializer),
        401: response_schema(401, ErrorResponseSerializer),
    },
)

wechat_mini_login_schema_info = dict(
    tags=["user"],
    summary="wechat_mini_login",
    description="Login with code and return a token.",
    request=WechatLoginRequestSerializer,
    responses={
        200: response_schema(200, UserSerializer, many=False),
        400: response_schema(400, WechatLoginValidateErrorSerializer),
        500: response_schema(500, ErrorResponseSerializer),
    },
)

profile_schema_info = dict(
    tags=["user"],
    summary="user_profile",
    description="**PERMISSION**: Allows access only to authenticated users.",
    responses={
        200: response_schema(200, UserSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
    },
)
