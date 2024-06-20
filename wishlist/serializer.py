from rest_framework import serializers

from account.serializer import UserSerializer
from wishlist.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'
