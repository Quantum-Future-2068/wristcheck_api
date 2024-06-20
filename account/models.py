from django.contrib.auth.models import User
from django.db import models

from wristcheck_api.models import TimestampedModel


class Social(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    application_type = models.CharField(max_length=50, blank=False, default='wechat_mini_program')
    open_id = models.CharField(max_length=255, null=False, blank=False)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"open_id:{self.open_id}"