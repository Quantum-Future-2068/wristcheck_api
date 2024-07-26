from rest_framework import serializers

from account.models import Social, User


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    social_accounts = SocialSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ["password"]
