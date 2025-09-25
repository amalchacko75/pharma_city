from django.db import models
import uuid
from pharmacy.constant import DRUG_TYPE, PRESCRIPTION_STATUS_CHOICES


class Drug(models.Model):
    """
    Master table for drugs/medicines available in the hospital/pharmacy.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)
    brand = models.CharField(
        max_length=255, null=True, blank=True
    )
    formulation = models.CharField(
        max_length=100, null=True, blank=True
    )
    strength = models.CharField(
        max_length=50, null=True, blank=True
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    reorder_level = models.IntegerField(default=0)
    drug_type = models.CharField(
        max_length=32, choices=DRUG_TYPE, default='pain'
    )
    in_stock = models.BooleanField(default=True)


class InventoryBatch(models.Model):
    """
    Tracks stock of each drug in the pharmacy by batch.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    drug = models.ForeignKey(
        Drug, on_delete=models.CASCADE, related_name="batches"
    )
    batch_number = models.CharField(
        max_length=128, null=True, blank=True
    )
    qty_on_hand = models.IntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)


class Prescription(models.Model):
    """
    Represents a prescription created by a doctor/prescriber for a patient.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE
    )
    prescriber = models.ForeignKey(
        "accounts.AdminUser", null=True,
        on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=32,
        choices=PRESCRIPTION_STATUS_CHOICES,
        default="draft"
    )
    notes = models.TextField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PrescriptionItem(models.Model):
    """
    Represents individual drugs prescribed within a prescription.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    prescription = models.ForeignKey(
        Prescription, related_name="items", on_delete=models.CASCADE
    )
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=128, null=True, blank=True)
    frequency = models.CharField(max_length=128, null=True, blank=True)
    quantity = models.IntegerField()
    duration_days = models.IntegerField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)


class Dispensation(models.Model):
    """
    Records the dispensing of drugs by the pharmacist.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="dispensations"
    )
    pharmacist = models.ForeignKey(
        "accounts.AdminUser", null=True, on_delete=models.SET_NULL
    )
    dispensed_at = models.DateTimeField(auto_now_add=True)
    dispensed_qty = models.IntegerField()
    batch = models.ForeignKey(
        InventoryBatch, null=True, blank=True, on_delete=models.SET_NULL
    )
