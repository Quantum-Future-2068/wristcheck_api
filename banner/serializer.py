from rest_framework import serializers

from account.serializer import UserSerializer
from .models import Banner


class BannerSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=False)
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Banner
        fields = '__all__'
