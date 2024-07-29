from rest_framework import serializers

from account.models import Social, User
from wristcheck_api.settings import env


class SocialSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Social
        fields = "__all__"

    @staticmethod
    def get_avatar_url(obj):
        if obj.avatar_url:
            return f'{env.str("STATIC_DOMAIN")}/{obj.avatar_url}'
        return None


class UserSerializer(serializers.ModelSerializer):
    social_accounts = SocialSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ["password"]
