import re
from django.db.models import Q
from pharmacy.models import Pharmacy, PharmacyDrug
from rest_framework import serializers
from rapidfuzz import process, fuzz
from billing.utils.invoice_extractor import extract_invoice_drugs


class PharmacyDrugSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="drug.id", read_only=True)
    drug_name = serializers.CharField(source="drug.name", read_only=True)
    brand = serializers.CharField(source="drug.brand", read_only=True)
    formulation = serializers.CharField(source="drug.formulation", read_only=True)
    strength = serializers.CharField(source="drug.strength", read_only=True)

    class Meta:
        model = PharmacyDrug
        fields = [
            "id", "drug_name", "brand", "formulation", "strength",
            "actual_rate", "sell_rate", "discount_percentage", "cgst", "sgst",
        ]


class InvoiceExtractSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # ✅ Ensure logged-in pharmacist
        if not user or getattr(user, "role", None) != "pharmacist":
            raise serializers.ValidationError("Only pharmacists can perform this action.")

        # ✅ Fetch pharmacy linked to this user
        try:
            pharmacy = Pharmacy.objects.get(user=user)
        except Pharmacy.DoesNotExist:
            raise serializers.ValidationError("No pharmacy found for this pharmacist.")

        file = attrs.get("file")

        # 🧠 Step 1: OCR extraction
        extracted_names = extract_invoice_drugs(file)
        cleaned = [name.strip() for name in extracted_names if name.strip()]
        attrs["extracted_names"] = cleaned

        # 🧠 Step 2: Partial matching (icontains)
        name_query = Q()
        for name in cleaned:
            tokens = [t for t in re.split(r"\s+", name) if len(t) > 2]
            for token in tokens:
                name_query |= Q(drug__name__icontains=token)
        
        query = Q(pharmacy=pharmacy) & name_query

        # 🧠 Step 3: Fuzzy matching (RapidFuzz)
        db_names = list(
            PharmacyDrug.objects.filter(pharmacy=pharmacy)
            .values_list("drug__name", flat=True)
        )
        fuzzy_q = Q()
        unmatched = []

        for extracted in cleaned:
            match, score, _ = process.extractOne(
                extracted, db_names, scorer=fuzz.partial_ratio
            )
            if score >= 80:
                fuzzy_q |= Q(drug__name__iexact=match, pharmacy=pharmacy)
            else:
                unmatched.append(extracted)

        # 🧠 Step 4: Combine both queries
        final_matches = PharmacyDrug.objects.filter(query | fuzzy_q).distinct()

        # 🧠 Step 5: Determine unmatched items
        matched_names = [d.drug.name.lower() for d in final_matches]
        final_unmatched = [
            n for n in cleaned
            if not any(n.lower() in m for m in matched_names)
        ]

        attrs["matched_drugs"] = final_matches
        attrs["unmatched"] = final_unmatched
        return attrs

    def to_representation(self, instance):
        return {
            "invoice_filename": instance["file"].name,
            "extracted_drug_names": instance["extracted_names"],
            "matched_drugs": PharmacyDrugSerializer(
                instance["matched_drugs"], many=True
            ).data,
            "unmatched_items": instance["unmatched"],
        }
