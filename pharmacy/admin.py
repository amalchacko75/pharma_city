from django.contrib import admin

from pharmacy.models import (
    Dispensation, Drug, InventoryBatch,
    MedicineOrder, MedicineOrderItem, Pharmacy, PharmacyDrug,
    Prescription, PrescriptionItem
)


admin.site.register(Drug)
admin.site.register(InventoryBatch)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
admin.site.register(Dispensation)
admin.site.register(Pharmacy)
admin.site.register(MedicineOrder)
admin.site.register(MedicineOrderItem)
admin.site.register(PharmacyDrug)
