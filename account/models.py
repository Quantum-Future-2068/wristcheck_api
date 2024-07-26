from django.core.exceptions import ValidationError

from wristcheck_api.models import TimestampedModel

import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    def create(self, **kwargs):
        email = kwargs.get("email")
        if email and self.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return super().create(**kwargs)

    def update(self, **kwargs):
        email = kwargs.get("email")
        if email and self.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return super().update(**kwargs)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(id=uuid.uuid4(), email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, editable=False)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    def clean(self):
        if (
            self.email
            and User.objects.exclude(id=self.id).filter(email=self.email).exists()
        ):
            raise ValidationError("A user with this email already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(User, self).save(*args, **kwargs)


class Social(TimestampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_accounts"
    )
    application_type = models.CharField(max_length=50, blank=False, default="mp")
    open_id = models.CharField(max_length=255, null=False, blank=False)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"open_id:{self.open_id}"
