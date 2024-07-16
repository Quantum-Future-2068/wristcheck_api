from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from utils.schemas import (
    response_schema,
    parameter_page_size,
    parameter_ordering,
    parameter_search,
)
from utils.serializers import ErrorResponseSerializer
from wishlist.serializers.models import WishlistSerializer
from wishlist.serializers.serializers import (
    WishlistAddRequestSerializer,
    FavoriteStatusRequestSerializer,
    FavoriteStatusResponseSerializer,
    WishlistAddValidateErrorSerializer,
)
from wristcheck_api.constants import (
    DEFAULT_PAGE_SIZE,
    DEFAULT_MAX_PAGE_SIZE,
    USUAL_ORDERING_FIELDS,
    USUAL_ORDERING,
)

tags = ["wishlist"]

list_schema_info = dict(
    tags=tags,
    summary="wishlist_list",
    description="**PERMISSION**: Allows access only to admin users.",
    parameters=[
        parameter_page_size(),
        parameter_ordering(USUAL_ORDERING_FIELDS, default=f"-{USUAL_ORDERING}"),
        parameter_search(["watch_id", "username"]),
    ],
    responses={
        200: response_schema(200, WishlistSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

retrieve_schema_info = dict(
    tags=tags,
    summary="wishlist_retrieve",
    description="**PERMISSION**: Allows access only to owner or admin users.",
    responses={
        200: response_schema(200, WishlistSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

destroy_schema_info = dict(
    tags=tags,
    summary="wishlist_destroy",
    description="**PERMISSION**: Allows access only to owner or admin users.",
    responses={
        204: response_schema(204, WishlistSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

add_schema_info = dict(
    tags=tags,
    summary="wishlist_add",
    description="**PERMISSION**: Allows access only to authenticated users.",
    request=WishlistAddRequestSerializer,
    responses={
        201: response_schema(201, WishlistSerializer, many=False),
        400: response_schema(400, WishlistAddValidateErrorSerializer),
        401: response_schema(401, ErrorResponseSerializer),
    },
)

my_own_schema_info = dict(
    tags=tags,
    summary="wishlist_my_own",
    description="**PERMISSION**: Allows access only to authenticated users.",
    responses={
        200: response_schema(200, WishlistSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
    },
)

favorite_status_schema_info = dict(
    tags=tags,
    summary="favorite_status",
    description="""Usage scenario: Browse the recent page to display the favorite status of the watch.<br>
    **PERMISSION**: Allows access only to authenticated users.
    """,
    parameters=[
        OpenApiParameter(
            name="watch_ids",
            type=OpenApiTypes.STR,
            description='Comma separated watch ids. Example: "?watch_ids=1&watch_ids=2"',
            required=True,
        )
    ],
    request=FavoriteStatusRequestSerializer,
    responses={
        200: FavoriteStatusResponseSerializer(many=True),
        400: response_schema(400, FavoriteStatusRequestSerializer),
        401: response_schema(401, ErrorResponseSerializer),
    },
)
