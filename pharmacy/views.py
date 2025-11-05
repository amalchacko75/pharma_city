# pharmacy/views.py

from pharmacy.serializer import (
    DrugSerializer, MedicineOrderCreateSerializer, MedicineOrderSerializer,
    PharmacyDrugCreateSerializer, PharmacyDrugListSerializer
)
from rest_framework import generics, permissions, filters
# from rest_framework.response import Response
from rest_framework import viewsets
from .models import Drug, MedicineOrder, Pharmacy, PharmacyDrug


class MedicineOrderViewSet(viewsets.ModelViewSet):
    """
    Handles listing, creating, updating, and deleting medicine orders.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = MedicineOrder.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MedicineOrderCreateSerializer
        return MedicineOrderSerializer


class PharmacyDrugViewSet(viewsets.ModelViewSet):
    """
    CRUD API for managing PharmacyDrug records.
    - GET /pharmacy-drugs/ → list all drugs for current pharmacist
    - GET /pharmacy-drugs/{id}/ → retrieve single drug
    - POST /pharmacy-drugs/ → add new drug
    - PUT /pharmacy-drugs/{id}/ → update existing drug
    - DELETE /pharmacy-drugs/{id}/ → delete drug
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["drug__name", "drug__brand", "drug__formulation"]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) != "pharmacist":
            return PharmacyDrug.objects.none()

        try:
            pharmacy = Pharmacy.objects.get(user=user)
        except Pharmacy.DoesNotExist:
            return PharmacyDrug.objects.none()

        return PharmacyDrug.objects.filter(
            pharmacy=pharmacy
        ).select_related("drug")

    def get_serializer_class(self):
        # Choose serializer based on method
        if self.action in ["create", "update", "partial_update"]:
            return PharmacyDrugCreateSerializer
        return PharmacyDrugListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class DrugViewSet(viewsets.ModelViewSet):
    """
    Full CRUD API for the global Drug master table.
    Supports search, filtering, and ordering.
    """
    queryset = Drug.objects.all()
    serializer_class = DrugSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "brand", "formulation", "strength"]
    ordering_fields = ["name", "unit_price", "drug_type"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = Drug.objects.all()

        # Optional filters via query params
        drug_type = self.request.query_params.get("drug_type")
        in_stock = self.request.query_params.get("in_stock")

        if drug_type:
            queryset = queryset.filter(drug_type=drug_type)
        if in_stock in ["true", "false"]:
            queryset = queryset.filter(in_stock=(in_stock == "true"))

        return queryset
