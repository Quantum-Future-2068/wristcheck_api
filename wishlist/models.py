from django.db import models

from account.models import User
from wristcheck_api.models import TimestampedModel, SoftDeletedModel


class Wishlist(TimestampedModel, SoftDeletedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch_id = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = ("user", "watch_id")
        ordering = ["-updated_at"]
