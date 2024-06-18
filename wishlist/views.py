from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from drf.pagination import CustomPagination
from wishlist.models import Wishlist
from wishlist.serializer import WishlistSerializer
from wristcheck_api.constants import USUAL_ORDERING_FIELDS, USUAL_ORDERING
from wristcheck_api.permission import GetPermissionByModelActionMixin, IsOwnerOrAdminUser, IsOwner


class WishlistViewSet(
    GetPermissionByModelActionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    authentication_classes = (
        SessionAuthentication,
        TokenAuthentication
    )
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsOwnerOrAdminUser],
        'create': [IsAdminUser],
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
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Which field to use when ordering the results.',
                enum=USUAL_ORDERING_FIELDS,
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=['POST'], detail=False)
    def add(self, request):
        """Add watch to wishlist

        :param request: {"watch_id": "123"}
        :return: {"user": 1, "watch_id": "123"}
        """
        request.data['user'] = request.user.id
        return super().create(request)

    @action(methods=['GET'], detail=False)
    def my_own(self, request):
        """Get my own wishlist

        :param request:
        :return: json, example: [{"user": 1, "watch_id": "123"}]
        """
        self.queryset = self.get_queryset().filter(user=request.user)
        return self.list(request)
