from django.contrib import admin
from django.contrib.admin import ModelAdmin

from account.admin import get_all_fields
from track.models import WatchVisitRecord


@admin.register(WatchVisitRecord)
class WatchVisitRecordAdmin(ModelAdmin):
    list_display = get_all_fields(WatchVisitRecord)
    list_display_links = list_display
    list_filter = []
    search_fields = ["user_id", "watch_id"]
