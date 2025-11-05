from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pharmacy.views import (
    DrugViewSet, MedicineOrderViewSet,
    PharmacyDrugViewSet
)

router = DefaultRouter()
router.register("orders", MedicineOrderViewSet, basename="medicine-orders")
router.register("drugs", DrugViewSet, basename="drugs-details")
router.register(
    "pharmacy-drugs",
    PharmacyDrugViewSet,
    basename="pharmacy_drugs_details"
)

urlpatterns = [
    # Regular path-based routes
    path("", include(router.urls)),
]
