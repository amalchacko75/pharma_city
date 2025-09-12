from django.db import models
import uuid


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=32, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    facility = models.ForeignKey("core.Facility", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
