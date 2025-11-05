from django.db import models
import uuid

from django.forms import ValidationError

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

    class Meta:
        unique_together = ("name", "brand")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.drug_type})"


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
        "accounts.AdminUser",
        on_delete=models.CASCADE,
        related_name='prescriptions_as_patient'
    )
    prescriber = models.ForeignKey(
        "accounts.AdminUser", null=True,
        on_delete=models.SET_NULL,
        related_name='prescriptions_as_prescriber'
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


class Pharmacy(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=255)
    address = models.TextField()

    city = models.ForeignKey(
        "core.City", on_delete=models.CASCADE,
        related_name="pharmacies"
    )
    user = models.ForeignKey(
        "accounts.AdminUser",
        null=True, on_delete=models.SET_NULL,
        related_name="pharmacy_user"
    )

    # Coordinates
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    open_hours = models.CharField(max_length=255, blank=True, null=True)
    is_24x7 = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.city})"

    def get_coordinates(self):
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None


class MedicineOrder(models.Model):
    """
    Represents an order placed by a patient for one or more medicines.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "accounts.AdminUser",
        on_delete=models.CASCADE
    )
    pharmacy = models.ForeignKey(
        "pharmacy.Pharmacy",
        on_delete=models.SET_NULL, null=True
    )
    prescription = models.ForeignKey(
        "pharmacy.Prescription",
        on_delete=models.SET_NULL,
        null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("dispensed", "Dispensed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )

    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=["total_amount"])

    def __str__(self):
        return f"Order {self.id} by {self.patient.email}"


class MedicineOrderItem(models.Model):
    """
    Represents each drug item in a patient's medicine order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        MedicineOrder,
        related_name="items",
        on_delete=models.CASCADE
    )
    drug = models.ForeignKey("pharmacy.Drug", on_delete=models.PROTECT)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.drug.unit_price
        super().save(*args, **kwargs)
        self.order.calculate_total()


class Appointment(models.Model):
    """
    Represents a booking between a patient and a doctor.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "accounts.AdminUser", on_delete=models.CASCADE,
        related_name='appoinment_as_patient'
    )
    doctor = models.ForeignKey(
        "accounts.AdminUser",
        limit_choices_to={"role": "doctor"},
        on_delete=models.CASCADE,
        related_name='appoinment_as_doctor'
    )
    facility = models.ForeignKey(
        "core.Facility", on_delete=models.SET_NULL, null=True
    )
    appointment_date = models.DateTimeField()
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=[
            ("requested", "Requested"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("completed", "Completed"),
        ],
        default="requested"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.email} → {self.doctor.name} ({self.status})"


class PharmacyDrug(models.Model):
    """
    Pharmacy-specific pricing and tax information for each drug.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(
        'Pharmacy',
        on_delete=models.CASCADE,
        related_name='pharmacy_drugs'
    )

    drug = models.ForeignKey(
        'Drug',
        on_delete=models.CASCADE,
        related_name='pharmacy_prices'
    )

    # Pricing fields
    actual_rate = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Base purchase price"
    )
    sell_rate = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Price sold to customer"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )

    # Tax fields
    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Stock status
    in_stock = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pharmacy', 'drug')

    def __str__(self):
        return f"{self.pharmacy.name} - {self.drug.name}"

    @property
    def total_tax(self):
        """Return total GST percentage (CGST + SGST)."""
        return self.cgst + self.sgst

    @property
    def final_price(self):
        """
        Compute final price after discount and adding taxes.
        Formula: (sell_rate - discount) + taxes
        """
        discounted = self.sell_rate * (1 - self.discount_percentage / 100)
        taxed = discounted * (1 + (self.total_tax / 100))
        return round(taxed, 2)
