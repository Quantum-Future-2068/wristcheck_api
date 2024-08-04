from django.contrib.admin import ModelAdmin

from account.models import Social
from django.contrib import admin
from .models import User


def get_all_fields(model, exclude=None):
    if not exclude:
        exclude = []
    return [
        field.name
        for field in model._meta.get_fields()
        if not field.many_to_many
        and not field.one_to_many
        and field.name not in exclude
    ]


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = get_all_fields(User, exclude=["password"])
    list_display_links = list_display
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["id", "username", "email"]


@admin.register(Social)
class SocialAdmin(ModelAdmin):
    list_display = get_all_fields(Social)
    list_display_links = list_display
    search_fields = ["openid"]
