from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class LoginValidateErrorSerializer(serializers.Serializer):
    username = serializers.ListSerializer(child=serializers.CharField(), required=False)
    password = serializers.ListSerializer(child=serializers.CharField(), required=False)


class WechatLoginRequestSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)


class WechatLoginValidateErrorSerializer(serializers.Serializer):
    code = serializers.ListSerializer(child=serializers.CharField(), required=False)


class WechatProfilePostSerializer(serializers.Serializer):
    nickname = serializers.CharField(required=False)
    avatar_url = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get("nickname") and not attrs.get("avatar_url"):
            raise ValidationError(
                "At least one of 'nickname' or 'avatar_url' must be provided."
            )
        return super().validate(attrs)
