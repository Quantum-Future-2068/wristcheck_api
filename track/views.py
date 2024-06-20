# views.py
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.mixins import CustomCreateModelMixin
from utils.pagination import CustomPagination
from wristcheck_api.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from utils.permission import CustomGetPermissionMixin, IsOwnerOrAdminUser
from .models import WatchVisitRecord
from .serializer import WatchVisitRecordSerializer


class WatchVisitRecordViewSet(
    CustomGetPermissionMixin,
    CustomCreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = WatchVisitRecord.objects.all()
    serializer_class = WatchVisitRecordSerializer
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsOwnerOrAdminUser],
        'destroy': [IsAdminUser],
        'add': [IsAuthenticated],
        'analytics': [IsAdminUser],
        'my_own': [IsAuthenticated]
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'watch_id']
    search_fields = ['user_id', 'watch_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary='track_watch_visit_list',
        description='**PERMISSION**: Allows access only to admin users.',
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Which field to use when ordering the results. default: -created_at',
                enum=['created_at'],
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
                description=f'Filter results by **watch_id** or **user_id**. ',
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
                        'detail': {
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
                        'detail': {
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
        summary='track_watch_visit_retrieve',
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
                        'detail': {
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
                        'detail': {
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
        summary='track_watch_visit_retrieve',
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
                        'detail': {
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
                        'detail': {
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
        summary='track_watch_visit_add',
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
                        'detail': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        summary='track_watch_visit_my_own',
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
                        'detail': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='my_own')
    def my_own(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().filter(user=request.user)
        return self.list(request)

    @extend_schema(
        summary='track_watch_visit_analytics',
        description="""
        **PERMISSION**: Allows access only to authenticated users.
        
        Obtain the distribution of the number of times a user visits watch over a period of time
        
        eg: GET /watch-visit/analytics/?user_id=1&period=month&page=1&page_size=2
        """,
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.STR,
                description='Which field to filter by.',
                required=False
            ),
            OpenApiParameter(
                name='period',
                type=OpenApiTypes.STR,
                description=f'Which field to filter by',
                required=False,
                enum=['day', 'week', 'month', 'quarter', 'year'],
                default='month',
            ),
        ],
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'count': {
                            'type': 'integer',
                            'example': 1
                        },
                        'next': {
                            'type': 'string',
                            'nullable': True,
                            'example': None
                        },
                        'previous': {
                            'type': 'string',
                            'nullable': True,
                            'example': None
                        },
                        'results': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {
                                        'type': 'integer',
                                        'example': 1
                                    },
                                    'watch_id': {
                                        'type': 'string',
                                        'example': '123'
                                    },
                                    'count': {
                                        'type': 'integer',
                                        'example': 1
                                    }
                                }
                            }
                        }
                    }
                },
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'detail': {
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
                        'detail': {
                            'type': 'string',
                            'example': 'You do not have permission to perform this action.'
                        }
                    }
                },
                description='Forbidden'
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request, *args, **kwargs):
        period = request.data.get('period', 'month')
        now = timezone.now()
        start_time_map = dict(
            day=now - timedelta(days=1),
            week=now - timedelta(days=7),
            month=now - timedelta(days=30),
            quarter=now - timedelta(days=90),
            year=now - timedelta(days=365)
        )
        self.queryset = self.get_queryset().filter(
            created_at__gte=start_time_map.get(period, start_time_map['month'])
        )
        self.queryset = self.filter_queryset(self.get_queryset())
        product_visits = self.queryset.values('watch_id').annotate(count=Count('id')).order_by('-count')
        page = self.paginate_queryset(product_visits)
        return self.get_paginated_response(page)
