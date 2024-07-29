from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ValidationNonFieldErrorSerializer(serializers.Serializer):
    non_field_errors = serializers.ListSerializer(
        child=serializers.CharField(), required=False
    )
