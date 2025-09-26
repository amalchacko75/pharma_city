from django.contrib import admin

from pharmacy.models import (
    Dispensation, Drug, InventoryBatch, Pharmacy,
    Prescription, PrescriptionItem
)


admin.site.register(Drug)
admin.site.register(InventoryBatch)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
admin.site.register(Dispensation)
admin.site.register(Pharmacy)
