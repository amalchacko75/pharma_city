from chatbot.constant import SYMPTOM_TO_TYPE
from chatbot.registry import register_intent
from pharmacy.models import Drug
from rapidfuzz import process  # commonly used to match string contents.


@register_intent("drug_info")
def get_pharmacy_info(user_input: str):
    """Return available drugs dynamically from DB."""
    drugs = Drug.objects.all()[:5]
    if not drugs:
        return "Sorry, no drugs available right now."
    return "Available drugs: " + ", ".join(d.name for d in drugs)


@register_intent("drug_query")
def check_drug_availability(user_input: str):
    """Check if a particular drug is available in the store."""
    normalized = user_input.lower()

    # Try to extract the drug name by looking for known drug matches
    for drug in Drug.objects.all():
        if drug.name.lower() in normalized:
            return (
                f"✅ Yes, {drug.name} \
                    is available at {drug.unit_price} per unit."
            )

    return "❌ Sorry, that drug is not currently available in our store."


@register_intent("symptom_query")
def suggest_drug_for_symptom(user_input: str):
    """Suggest drugs based on symptoms and show availability."""
    normalized = user_input.lower().split()

    matches = []  # (drug_type, score)
    for word in normalized:
        result = process.extractOne(word, SYMPTOM_TO_TYPE.keys())
        if result:
            match, score, _ = result
            if score >= 80:  # confident match
                matches.append((SYMPTOM_TO_TYPE[match], score))

    if not matches:
        return "❓ Sorry, I couldn’t recognize the symptoms clearly."

    # Select best-scoring match (or ties within 5 points)
    best_score = max(score for _, score in matches)
    chosen_types = {
        drug_type for drug_type, 
        score in matches if best_score - score <= 5
    }

    responses = []
    for drug_type in chosen_types:
        drugs = Drug.objects.filter(drug_type=drug_type)[:5]

        if not drugs.exists():
            responses.append(f"⚠️ No {drug_type.title()} drugs available.")
            continue

        drug_statuses = []
        for d in drugs:
            status = (
                "✅ Available" if getattr(d, "in_stock", True) else
                "❌ Out of stock"
            )
            drug_statuses.append(f"{d.name} ({status})")

        responses.append(
            f"💊 {drug_type.title()} drugs: " + " | ".join(drug_statuses)
        )

    return " || ".join(responses)


@register_intent("drug_usage")
def check_drug_usage(user_input: str):
    """Check if a particular drug is available in the store."""
    normalized = user_input.lower()

    # Try to extract the drug name by looking for known drug matches
    for drug in Drug.objects.all():
        if drug.name.lower() in normalized:
            return f" {drug.name} is commonly used for {drug.formulation}"

    return "❌ Sorry, that drug is not currently available in our store."
