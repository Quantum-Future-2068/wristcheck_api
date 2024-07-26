from django.contrib.auth.models import User, AnonymousUser
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.settings import api_settings


class CustomGetPermissionMixin:
    """
    根据view类定义的permission_classes_map字典控制权限, 例如:

    class UserViewSet(CustomGetPermissionMixin, ReadOnlyModelViewSet):

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
            if hasattr(obj, "user"):
                return obj.user == request.user
            else:
                return obj == request.user
