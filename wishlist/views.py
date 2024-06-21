from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.mixins import CustomCreateModelMixin
from utils.pagination import CustomPagination
from wishlist.models import Wishlist
from wishlist.schemas import (
    list_schema_info,
    retrieve_schema_info,
    destroy_schema_info,
    add_schema_info,
    my_own_schema_info,
)
from wishlist.serializers.models import WishlistSerializer
from wishlist.serializers.serializers import WishlistAddRequestSerializer
from wristcheck_api.constants import USUAL_ORDERING_FIELDS, USUAL_ORDERING
from utils.permission import CustomGetPermissionMixin, IsOwnerOrAdminUser


class WishlistViewSet(
    CustomGetPermissionMixin,
    CustomCreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        "list": [IsAdminUser],
        "retrieve": [IsOwnerOrAdminUser],
        "destroy": [IsOwnerOrAdminUser],
        "add": [IsAuthenticated],
        "my_own": [IsAuthenticated],
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["watch_id", "user_id"]
    search_fields = ["watch_id", "user__name"]
    ordering_fields = USUAL_ORDERING_FIELDS
    ordering = USUAL_ORDERING

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
    @action(methods=["POST"], detail=False)
    def add(self, request, *args, **kwargs):
        serializer = WishlistAddRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(user=request.user.id, watch_id=request.data.get("watch_id"))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(**my_own_schema_info)
    @action(methods=["GET"], detail=False)
    def my_own(self, request):
        self.queryset = self.get_queryset().filter(user=request.user)
        return self.list(request)
