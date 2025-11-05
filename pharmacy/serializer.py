# pharmacy/serializers.py

from pharmacy.models import (
    Drug, MedicineOrder, MedicineOrderItem,
    Pharmacy, PharmacyDrug, Prescription
)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class MedicineOrderItemSerializer(serializers.ModelSerializer):
    drug_name = serializers.ReadOnlyField(source='drug.name')

    class Meta:
        model = MedicineOrderItem
        fields = ['id', 'drug', 'drug_name', 'quantity', 'subtotal']
        read_only_fields = ['subtotal', 'id']


class MedicineOrderCreateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineOrderItem
        fields = ['drug', 'quantity']


class MedicineOrderSerializer(serializers.ModelSerializer):
    items = MedicineOrderItemSerializer(many=True, read_only=True)
    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.name')

    class Meta:
        model = MedicineOrder
        fields = [
            'id', 'patient', 'pharmacy', 'pharmacy_name',
            'prescription', 'status', 'total_amount',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'status', 'total_amount']


class MedicineOrderCreateSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = MedicineOrderCreateItemSerializer(many=True)
    pharmacy = serializers.PrimaryKeyRelatedField(
        queryset=Pharmacy.objects.all()
    )
    prescription = serializers.PrimaryKeyRelatedField(
        queryset=Prescription.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = MedicineOrder
        fields = ['patient', 'pharmacy', 'prescription', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = MedicineOrder.objects.create(**validated_data)

        for item_data in items_data:
            MedicineOrderItem.objects.create(order=order, **item_data)

        order.calculate_total()
        return order


class PharmacyDrugListSerializer(serializers.ModelSerializer):
    drug_name = serializers.CharField(
        source="drug.name", read_only=True
    )
    brand = serializers.CharField(
        source="drug.brand", read_only=True
    )
    formulation = serializers.CharField(
        source="drug.formulation", read_only=True
    )
    strength = serializers.CharField(
        source="drug.strength", read_only=True
    )

    class Meta:
        model = PharmacyDrug
        fields = [
            "id", "drug_name", "brand", "formulation", "strength",
            "actual_rate", "sell_rate", "discount_percentage", "cgst", "sgst",
            "in_stock", "last_updated"
        ]


class PharmacyDrugCreateSerializer(serializers.ModelSerializer):
    """Create or update a PharmacyDrug record for the current pharmacy."""
    drug_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PharmacyDrug
        fields = [
            "drug_id", "actual_rate", "sell_rate", "discount_percentage",
            "cgst", "sgst", "in_stock"
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or getattr(user, "role", None) != "pharmacist":
            raise serializers.ValidationError("Only pharmacists can add drugs.")

        try:
            pharmacy = Pharmacy.objects.get(user=user)
        except Pharmacy.DoesNotExist:
            raise serializers.ValidationError("No pharmacy found for this pharmacist.")

        drug_id = validated_data.pop("drug_id")

        pharmacy_drug, _ = PharmacyDrug.objects.update_or_create(
            pharmacy=pharmacy,
            drug_id=drug_id,
            defaults=validated_data
        )

        return pharmacy_drug

    def update(self, instance, validated_data):
        """
        Safely update PharmacyDrug fields without altering the related Drug.
        """
        # Prevent changing the drug association on update
        validated_data.pop("drug_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class DrugSerializer(serializers.ModelSerializer):
    """Serializer for global Drug master table."""
    class Meta:
        model = Drug
        fields = [
            "id", "name", "brand", "formulation",
            "strength", "unit_price", "drug_type", "in_stock"
        ]
