from django.contrib import admin
from django.contrib.admin import ModelAdmin

from account.admin import get_all_fields
from wishlist.models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    list_display = get_all_fields(Wishlist)
    list_display_links = list_display
    list_filter = []
    search_fields = ["user_id", "watch_id"]
