from django.db import models
from audit.constant import AUDIT_ACTION_CHOICES


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        'accounts.AdminUser',
        null=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=32, choices=AUDIT_ACTION_CHOICES)
    entity_type = models.CharField(max_length=128)
    entity_id = models.CharField(max_length=128, null=True, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
