from django.db import models


class AuditMixin(models.Model):
    """
    Abstract mixin that adds audit fields:
    - created_at: when the record was first created
    - updated_at: last time record was updated
    - created_by: user who created the record
    - updated_by: user who last updated the record
    """

    created_at = models.DateTimeField(
        auto_now_add=True, null=True, blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True
    )
    created_by = models.ForeignKey(
        'accounts.AdminUser',
        null=True,
        blank=True,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        'accounts.AdminUser',
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True
