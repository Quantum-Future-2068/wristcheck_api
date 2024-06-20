from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from utils.mixins import CustomCreateModelMixin
from utils.pagination import CustomPagination
from services.aliyun_sts import get_sts_token
from wristcheck_api.constants import USUAL_ORDERING_FIELDS, USUAL_ORDERING
from utils.permission import CustomGetPermissionMixin
from .models import Banner
from django.utils import timezone

from .serializer import BannerSerializer


class BannerViewSet(CustomGetPermissionMixin, CustomCreateModelMixin, viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_enabled', 'user_id', 'headline', 'subtitle']
    search_fields = ['headline', 'subtitle']
    ordering_fields = USUAL_ORDERING_FIELDS
    ordering = USUAL_ORDERING
    pagination_class = CustomPagination

    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsAdminUser],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'destroy': [IsAdminUser],
        'active_banners': [AllowAny],
        'sts_token': [IsAdminUser],
        'soft_destroy': [IsAdminUser],
    }

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active_banners(self, request):
        """获取有效的轮播图或视频"""
        self.queryset = Banner.objects.get_active_banners()
        return self.list(request)

    @action(detail=True, methods=['get'])
    def sts_token(self, request):
        """服务端生成STS临时访问凭证"""
        return Response(get_sts_token(), status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def soft_destroy(self, request, *args, **kwargs):
        """软删除"""
        partial = kwargs.pop('partial', True)
        request.data = dict(deleted_at=timezone.now())
        return self.update(request, *args, **kwargs, partial=partial)
