# views.py
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from drf.pagination import CustomPagination
from wristcheck_api.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from wristcheck_api.permission import GetPermissionByModelActionMixin, IsOwnerOrAdminUser
from .models import WatchVisitRecord
from .serializer import WatchVisitRecordSerializer


class WatchVisitRecordViewSet(GetPermissionByModelActionMixin, viewsets.ModelViewSet):
    queryset = WatchVisitRecord.objects.all()
    serializer_class = WatchVisitRecordSerializer
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsOwnerOrAdminUser],
        'create': [IsAdminUser],
        'destroy': [IsAdminUser],
        'add': [IsAuthenticated],
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'watch_id']
    search_fields = ['user_id', 'watch_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Which field to use when ordering the results.',
                enum=['created_at'],
                required=False
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description=f'Number of results to return per page. Maximum value is {DEFAULT_MAX_PAGE_SIZE}.',
                required=False,
                default=DEFAULT_PAGE_SIZE,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request, *args, **kwargs):
        """Add watch visit record

        :param request: {"watch_id": "123"}
        :return: {"user": 1, "watch_id": "123"}
        """
        request.data['user'] = request.user.id
        return super().create(request)

    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request, *args, **kwargs):
        """
        获取一段时间内用户访问watch的次数分布情况

        查询参数：
        - `period`: 分析数据的时间范围，可选值为 'day', 'week', 'month', 'quarter', 'year'。

        例如: GET /watch-visit/analytics/?user_id=1&period=month&page=1&page_size=2
        """
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

    @action(detail=False, methods=['get'], url_path='my_own')
    def my_own(self, request, *args, **kwargs):
        """Get my own visit record

        :param request:
        :return: json, example: [{"user": 1, "watch_id": "123"}]
        """
        self.queryset = self.get_queryset().filter(user=request.user)
        return self.list(request)
