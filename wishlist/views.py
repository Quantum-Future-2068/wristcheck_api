from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from wishlist.models import Wishlist
from wishlist.serializer import WishlistSerializer
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
        'destroy': [IsAdminUser],
        'add': [IsAuthenticated]
    }

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
