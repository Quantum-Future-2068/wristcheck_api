from django.contrib.auth.models import User
from django.db.models import Q

from django.db import models
from django.utils import timezone


class BannerManager(models.Manager):
    def get_active_banners(self):
        now = timezone.now()
        return (
            self.filter(is_enabled=True, deleted_at__isnull=True, start_date__lte=now)
            .filter(Q(end_date__gte=now) | Q(end_date__isnull=True))
            .order_by("order")
        )


class Banner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255, blank=False, null=False)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    banner_link = models.CharField(max_length=255, blank=False, null=False)
    is_enabled = models.BooleanField(default=True)
    start_date = models.DateTimeField(blank=False, null=False, default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # asc
    deleted_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BannerManager()

    @property
    def is_active(self):
        now = timezone.now()
        return (
            self.is_enabled
            and self.deleted_at is None
            and self.start_date <= now <= (self.end_date if self.end_date else now)
        )

    def __str__(self):
        return self.headline
