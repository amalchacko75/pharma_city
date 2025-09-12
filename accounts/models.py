# from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from accounts.constant import ADMIN_ROLE_CHOICES


class AdminUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=32, choices=ADMIN_ROLE_CHOICES)
    facility = models.ForeignKey(
        "core.Facility", null=True,
        blank=True, on_delete=models.SET_NULL
    )
