from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from track.models import WatchVisitRecord
from wishlist.models import Wishlist


class WatchVisitRecordSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField(method_name="get_in_wishlist")

    class Meta:
        model = WatchVisitRecord
        fields = "__all__"

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_in_wishlist(self, obj):
        user = self.context["request"].user
        return (
            Wishlist.objects.filter(user=user, watch_id=obj.watch_id)
            .filter(deleted_at__isnull=True)
            .exists()
        )
