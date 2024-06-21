from drf_spectacular.utils import OpenApiResponse

from utils.serializers import ErrorResponseSerializer

status_code_schema_map = {
    200: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=serializer_class(many=many),
        description='Successful Response'
    ),
    201: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=serializer_class(many=many),
        description='HTTP Created Successful Response'
    ),
    204: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=None,
        description='HTTP No Content Successful Response'
    ),
    400: lambda serializer_class, many=True, *args, **kwargs: OpenApiResponse(
        response=serializer_class(many=many),
        description='Validation Error'
    ),
    401: lambda *args, **kwargs: OpenApiResponse(
        response=ErrorResponseSerializer,
        description='Valid authentication credentials were not provided.'
    ),
    403: lambda *args, **kwargs: OpenApiResponse(
        response=ErrorResponseSerializer,
        description='You do not have permission to perform this action.'
    ),
    500: lambda *args, **kwargs: OpenApiResponse(
        response=ErrorResponseSerializer,
        description=kwargs.get('description', 'Internal Server Error. ')
    ),
}


def response_schema(status_code, serializer_class, many=True):
    return status_code_schema_map[status_code](serializer_class, many)

# def generate_response_schemas(status_code_infos):
#     schemas = {}
#     for status_code_info in status_code_infos.items():
#         status_code = status_code_info.get('status_code')
#         serializer_class = status_code_info.get('serializer_class')
#         many = status_code_info.get('many', True)
#         schemas[status_code] = generate_response_schema(status_code, serializer_class, many)
#     return schemas
