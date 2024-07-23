# models.py
from django.contrib.auth.models import User
from django.db import models

from wristcheck_api.models import TimestampedModel


class WatchVisitRecord(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch_id = models.CharField(max_length=255, null=False, blank=False)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-updated_at"]
