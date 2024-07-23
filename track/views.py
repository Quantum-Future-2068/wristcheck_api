# views.py
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.mixins import CustomCreateModelMixin
from utils.pagination import CustomPagination
from utils.permission import CustomGetPermissionMixin, IsOwnerOrAdminUser
from .models import WatchVisitRecord
from .schemas import (
    list_schema_info,
    retrieve_schema_info,
    destroy_schema_info,
    add_schema_info,
    my_own_schema_info,
    analytics_schema_info,
)
from .serializers.model import WatchVisitRecordSerializer
from .serializers.serializers import WatchVisitRecordAddRequestSerializer


class WatchVisitRecordViewSet(
    CustomGetPermissionMixin,
    CustomCreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = WatchVisitRecord.objects.all()
    serializer_class = WatchVisitRecordSerializer
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        "list": [IsAdminUser],
        "retrieve": [IsOwnerOrAdminUser],
        "destroy": [IsAdminUser],
        "add": [IsAuthenticated],
        "analytics": [IsAdminUser],
        "my_own": [IsAuthenticated],
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["user_id", "watch_id"]
    search_fields = ["user_id", "watch_id"]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]

    @extend_schema(**list_schema_info)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**retrieve_schema_info)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**destroy_schema_info)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(**add_schema_info)
    @action(detail=False, methods=["post"], url_path="add")
    def add(self, request, *args, **kwargs):
        serializer = WatchVisitRecordAddRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        visit_record, created = WatchVisitRecord.objects.get_or_create(
            user=request.user, watch_id=request.data["watch_id"]
        )
        if not created:
            visit_record.updated_at = timezone.now()
            visit_record.count += 1
            visit_record.save()

        serializer = self.get_serializer(visit_record)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(**my_own_schema_info)
    @action(detail=False, methods=["get"], url_path="my_own")
    def my_own(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().filter(user=request.user)
        return self.list(request)

    @extend_schema(**analytics_schema_info)
    @action(detail=False, methods=["get"], url_path="analytics")
    def analytics(self, request, *args, **kwargs):
        period = request.query_params.get("period", "month")
        now = timezone.now()
        start_time_map = dict(
            day=now - timedelta(days=1),
            week=now - timedelta(days=7),
            month=now - timedelta(days=30),
            quarter=now - timedelta(days=90),
            year=now - timedelta(days=365),
        )
        self.queryset = self.get_queryset().filter(
            created_at__gte=start_time_map.get(period, start_time_map["month"])
        )
        self.queryset = self.filter_queryset(self.get_queryset())
        product_visits = (
            self.queryset.values("watch_id")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        page = self.paginate_queryset(product_visits)
        return self.get_paginated_response(page)
