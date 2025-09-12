from django.contrib import admin

from pharmacy.models import (
    Dispensation, Drug, InventoryBatch,
    Prescription, PrescriptionItem
)


admin.site.register(Drug)
admin.site.register(InventoryBatch)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
admin.site.register(Dispensation)
