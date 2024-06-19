from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import mixins, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf.pagination import CustomPagination
from wishlist.models import Wishlist
from wishlist.serializer import WishlistSerializer
from wristcheck_api.constants import USUAL_ORDERING_FIELDS, USUAL_ORDERING, DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from wristcheck_api.permission import GetPermissionByModelActionMixin, IsOwnerOrAdminUser, IsOwner


class WishlistViewSet(
    GetPermissionByModelActionMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication
    )
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsOwnerOrAdminUser],
        'destroy': [IsOwnerOrAdminUser],
        'add': [IsAuthenticated]
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['watch_id', 'user__username']
    search_fields = ['watch_id', 'user__username']
    ordering_fields = USUAL_ORDERING_FIELDS
    ordering = USUAL_ORDERING

    @extend_schema(
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
            200: OpenApiResponse(
                response=serializer_class(many=True),
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            ),
            403: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'You do not have permission to perform this action.'
                        }
                    }
                },
                description='Forbidden'
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='wishlist_retrieve',
        description='**PERMISSION**: Allows access only to owner or admin users.',
        responses={
            200: OpenApiResponse(
                response=serializer_class(many=False),
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            ),
            403: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'You do not have permission to perform this action.'
                        }
                    }
                },
                description='Forbidden'
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary='wishlist_retrieve',
        description='**PERMISSION**: Allows access only to owner or admin users.',
        responses={
            204: OpenApiResponse(
                response=None,
                description='HTTP No Content Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            ),
            403: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'You do not have permission to perform this action.'
                        }
                    }
                },
                description='Forbidden'
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary='wishlist_add',
        description='**PERMISSION**: Allows access only to authenticated users.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'watch_id': {
                        'type': 'string',
                        'description': 'ID of the watch to be added to the wishlist',
                        'example': '123'
                    }
                },
                'required': ['watch_id']
            }
        },
        responses={
            201: OpenApiResponse(
                response=serializer_class(many=False),
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            )
        }
    )
    @action(methods=['POST'], detail=False)
    def add(self, request):
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        summary='wishlist_my_own',
        description='**PERMISSION**: Allows access only to authenticated users.',
        responses={
            200: OpenApiResponse(
                response=serializer_class(many=True),
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            )
        }
    )
    @action(methods=['GET'], detail=False)
    def my_own(self, request):
        self.queryset = self.get_queryset().filter(user=request.user)
        return self.list(request)
