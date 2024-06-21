from rest_framework import serializers


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
