from rest_framework import serializers


class WatchVisitRecordAddRequestSerializer(serializers.Serializer):
    watch_id = serializers.CharField(required=True)


class WatchVisitRecordAddValidateErrorSerializer(serializers.Serializer):
    watch_id = serializers.ListSerializer(child=serializers.CharField(), required=False)
