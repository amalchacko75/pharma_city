from django.db import models
import uuid

from billing.constant import PAYMENT_STATUS_CHOICES


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES,
        default="unpaid"
    )
    created_at = models.DateTimeField(auto_now_add=True)


# class Payment(models.Model):
#     METHOD_CHOICES = [("cash","Cash"),("card","Card"),("upi","UPI")]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
#     method = models.CharField(max_length=32, choices=METHOD_CHOICES)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     transaction_ref = models.CharField(max_length=255, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
