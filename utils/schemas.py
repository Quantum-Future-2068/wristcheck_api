from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter
from rest_framework import status

from utils.serializers import ErrorResponseSerializer
from wristcheck_api.constants import DEFAULT_MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE

status_code_schema_map = {
    status.HTTP_200_OK: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=serializer_class(many=many), description="Successful Response"
    ),
    status.HTTP_201_CREATED: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=serializer_class(many=many),
        description="HTTP Created Successful Response",
    ),
    status.HTTP_204_NO_CONTENT: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=None, description="HTTP No Content Successful Response"
    ),
    status.HTTP_400_BAD_REQUEST: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=serializer_class(many=many), description="Validation Error"
    ),
    status.HTTP_401_UNAUTHORIZED: lambda *args, **kwargs: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Valid authentication credentials were not provided.",
    ),
    status.HTTP_403_FORBIDDEN: lambda *args, **kwargs: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="You do not have permission to perform this action.",
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: lambda *args, **kwargs: OpenApiResponse(
        response=ErrorResponseSerializer,
        description=kwargs.get("description", "Internal Server Error. "),
    ),
}


def response_schema(status_code, serializer_class, many=True, *args, **kwargs):
    return status_code_schema_map[status_code](serializer_class, many, *args, **kwargs)


def parameter_ordering(ordering_fields, default=None):
    """
    :param ordering_fields: ["foo", "bar"]
    :param default: -foo | foo
    :return: OpenApiParameter instance
    """
    return OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=f"Which field to use when ordering the results. default: {default}",
        enum=ordering_fields,
        required=False,
    )


def parameter_page_size(maximum=DEFAULT_MAX_PAGE_SIZE, default=DEFAULT_PAGE_SIZE):
    return OpenApiParameter(
        name="page_size",
        type=OpenApiTypes.INT,
        description=f"Number of results to return per page. Maximum value is {maximum}.",
        required=False,
        default=default,
    )


def parameter_search(search_fields):
    description = "Filter results by" + "|".join(search_fields)
    return OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description=description,
        required=False,
    )
