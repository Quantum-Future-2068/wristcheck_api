# models.py
from django.contrib.auth.models import User
from django.db import models


class WatchVisitRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch_id = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
