from django.db import models
import uuid


class Facility(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    address = models.TextField(null=True, blank=True)


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")

    def __str__(self):
        return f"{self.name}, {self.state or ''}".strip(", ")
