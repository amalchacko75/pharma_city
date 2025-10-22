# from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from accounts.constant import ADMIN_ROLE_CHOICES
from accounts.mixins import AdminUserManager, AuditMixin


class AdminUser(AbstractBaseUser,
                PermissionsMixin,
                AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    role = models.CharField(max_length=32, choices=ADMIN_ROLE_CHOICES)
    facility = models.ForeignKey(
        "core.Facility", null=True,
        blank=True, on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AdminUserManager()

    def __str__(self):
        """
        Display the AdminUser as 'name (role)' in dropdowns and admin lists.
        If name is missing, show just the role.
        """
        if self.name:
            return f"{self.name} ({self.role})"
        return f"{self.role}"
