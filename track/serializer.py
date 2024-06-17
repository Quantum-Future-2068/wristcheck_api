from django.contrib.auth.models import User
from rest_framework import serializers

from track.models import WatchVisitRecord


class WatchVisitRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchVisitRecord
        fields = '__all__'
