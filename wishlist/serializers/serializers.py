from rest_framework import serializers


class WishlistAddRequestSerializer(serializers.Serializer):
    watch_id = serializers.CharField(required=True)


class WishlistAddValidateErrorSerializer(serializers.Serializer):
    watch_id = serializers.ListSerializer(child=serializers.CharField(), required=False)
