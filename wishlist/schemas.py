from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from track.serializers.model import WatchVisitRecordSerializer
from track.serializers.serializers import WatchVisitRecordAddValidateErrorSerializer
from utils.schemas import response_schema
from utils.serializers import ErrorResponseSerializer
from wishlist.serializers.serializers import WishlistAddRequestSerializer
from wristcheck_api.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE, USUAL_ORDERING_FIELDS

tags = ['wishlist']

list_schema_info = dict(
    tags=tags,
    summary='wishlist_list',
    description='**PERMISSION**: Allows access only to admin users.',
    parameters=[
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            description='Which field to use when ordering the results.',
            enum=USUAL_ORDERING_FIELDS,
            required=False
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            description=f'Number of results to return per page. Maximum value is {DEFAULT_MAX_PAGE_SIZE}.',
            required=False,
            default=DEFAULT_PAGE_SIZE,
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            description=f'Filter results by **watch_id** or **username**. ',
            required=False,
        )
    ],
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    }
)

retrieve_schema_info = dict(
    tags=tags,
    summary='wishlist_retrieve',
    description='**PERMISSION**: Allows access only to owner or admin users.',
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    }
)

destroy_schema_info = dict(
    tags=tags,
    summary='wishlist_destroy',
    description='**PERMISSION**: Allows access only to owner or admin users.',
    responses={
        204: response_schema(204, WatchVisitRecordSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    }
)

add_schema_info = dict(
    tags=tags,
    summary='wishlist_add',
    description='**PERMISSION**: Allows access only to authenticated users.',
    request=WishlistAddRequestSerializer,
    responses={
        201: response_schema(201, WatchVisitRecordSerializer, many=False),
        400: response_schema(400, WatchVisitRecordAddValidateErrorSerializer),
        401: response_schema(401, ErrorResponseSerializer),
    }
)

my_own_schema_info = dict(
    tags=tags,
    summary='wishlist_my_own',
    description='**PERMISSION**: Allows access only to authenticated users.',
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
    }
)
