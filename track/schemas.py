from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from track.serializers.model import WatchVisitRecordSerializer
from track.serializers.serializers import (
    WatchVisitRecordAddRequestSerializer,
    WatchVisitRecordAddValidateErrorSerializer,
)
from utils.schemas import (
    response_schema,
    parameter_page_size,
    parameter_ordering,
    parameter_search,
)
from utils.serializers import ErrorResponseSerializer

tags = ["track"]

list_schema_info = dict(
    tags=tags,
    summary="track_watch_visit_list",
    description="**PERMISSION**: Allows access only to admin users.",
    parameters=[
        parameter_page_size(),
        parameter_ordering(["created_at"], default="-created_at"),
        parameter_search(["watch_id", "user_id"]),
    ],
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

retrieve_schema_info = dict(
    tags=tags,
    summary="track_watch_visit_retrieve",
    description="**PERMISSION**: Allows access only to owner or admin users.",
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

destroy_schema_info = dict(
    tags=tags,
    summary="track_watch_visit_destroy",
    description="**PERMISSION**: Allows access only to owner or admin users.",
    responses={
        204: response_schema(204, WatchVisitRecordSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)

add_schema_info = dict(
    tags=tags,
    summary="track_watch_visit_add",
    description="**PERMISSION**: Allows access only to authenticated users.",
    request=WatchVisitRecordAddRequestSerializer,
    responses={
        201: response_schema(201, WatchVisitRecordSerializer, many=False),
        400: response_schema(400, WatchVisitRecordAddValidateErrorSerializer),
        401: response_schema(401, ErrorResponseSerializer),
    },
)

my_own_schema_info = dict(
    tags=tags,
    summary="track_watch_visit_my_own",
    description="**PERMISSION**: Allows access only to authenticated users.",
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=True),
        401: response_schema(401, ErrorResponseSerializer),
    },
)

analytics_schema_info = dict(
    tags=tags,
    summary="track_watch_visit_analytics",
    description="""
**PERMISSION**: Allows access only to admin users.

Obtain the distribution of the number of times a user visits watch over a period of time

eg: GET /watch-visit/analytics/?user_id=1&period=month&page=1&page_size=2""",
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=OpenApiTypes.STR,
            description="Which field to filter by.",
            required=False,
        ),
        OpenApiParameter(
            name="period",
            type=OpenApiTypes.STR,
            description=f"Which field to filter by",
            required=False,
            enum=["day", "week", "month", "quarter", "year"],
            default="month",
        ),
    ],
    responses={
        200: response_schema(200, WatchVisitRecordSerializer, many=False),
        401: response_schema(401, ErrorResponseSerializer),
        403: response_schema(403, ErrorResponseSerializer),
    },
)
