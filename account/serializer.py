from django.contrib.auth.models import User
from rest_framework import serializers

from account.models import Social


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    social = SocialSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ['password']
