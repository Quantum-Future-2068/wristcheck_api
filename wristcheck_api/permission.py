from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, BasePermission


class GetPermissionByModelActionMixin:
    """
    根据view类定义的permission_classes_map，动态设置权限, 例如:

    class UserViewSet(GetPermissionByModelActionMixin, viewsets.ReadOnlyModelViewSet):

        permission_classes_map = {
            'list': [IsAuthenticated],
            'retrieve': [IsAuthenticated],
            'create': [IsAuthenticated],
            'update': [IsAuthenticated],
            'destroy': [IsAuthenticated],
        }
    """

    def get_permissions(self):
        permissions = self.permission_classes_map.get(self.action, [AllowAny])
        return [permission() for permission in permissions]


class IsOwner(BasePermission):
    """
    Allows access only to owner.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj.id == request.user.id
        else:
            return obj.user == request.user


class IsOwnerOrSuperUser(BasePermission):
    """
    Allows access only to owner or superuser.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if isinstance(obj, User):
            return obj.id == request.user.id
        else:
            return obj.user == request.user


class IsOwnerOrAdminUser(BasePermission):
    """
    Allows access only to owner or admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if isinstance(obj, User):
            return obj.id == request.user.id
        else:
            return obj.user == request.user
