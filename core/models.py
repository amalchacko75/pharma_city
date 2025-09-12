from django.db import models
import uuid


class Facility(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    address = models.TextField(null=True, blank=True)
