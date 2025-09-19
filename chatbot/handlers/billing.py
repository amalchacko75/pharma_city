from chatbot.registry import register_intent
from billing.models import Invoice


@register_intent("billing")
def get_billing_status(user_input: str):
    invoice = Invoice.objects.last()
    if not invoice:
        return "No billing records found."
    return f"Latest invoice #{invoice.id} status: {invoice.status}"
