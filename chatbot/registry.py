# Central registry for all chatbot intent handlers
INTENT_REGISTRY = {}


def register_intent(tag):
    """Decorator to register an intent handler."""
    def decorator(func):
        INTENT_REGISTRY[tag] = func
        return func
    return decorator
