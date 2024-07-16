from rest_framework import serializers


class WishlistAddRequestSerializer(serializers.Serializer):
    watch_id = serializers.CharField(required=True)


class WishlistAddValidateErrorSerializer(serializers.Serializer):
    watch_id = serializers.ListSerializer(child=serializers.CharField(), required=False)


class FavoriteStatusRequestSerializer(serializers.Serializer):
    watch_ids = serializers.ListField(child=serializers.CharField(), required=True)


class FavoriteStatusResponseSerializer(serializers.Serializer):
    watch_id = serializers.CharField()
    favorite = serializers.BooleanField()
