from django.contrib.auth.models import User
from django.db import models

from wristcheck_api.models import TimestampedModel


class Wishlist(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch_id = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        unique_together = ('user', 'watch_id')

    def __str__(self):
        return f'{self.user.username} - {self.watch_id}'
