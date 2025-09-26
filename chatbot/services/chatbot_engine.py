import os
import random
import pickle
import json
import inspect

from chatbot.registry import INTENT_REGISTRY
import chatbot.handlers  # noqa: F401
from chatbot.services.redis_client import (
    clear_last_intent, get_last_intent, set_last_intent
)

model = None
vectorizer = None
intents = None


def load_artifacts():
    global model, vectorizer, intents
    if model is None or vectorizer is None or intents is None:
        base_path = os.path.join(os.path.dirname(__file__), "../ml")

        with open(os.path.join(base_path, "model.pkl"), "rb") as f:
            model = pickle.load(f)

        with open(os.path.join(base_path, "vectorizer.pkl"), "rb") as f:
            vectorizer = pickle.load(f)

        with open(os.path.join(base_path, "intents.json")) as f:
            intents = json.load(f)


def get_response(
        user_input: str,
        user_id: str = "default", lat=None, lng=None):
    load_artifacts()

    # 1. Check follow-up
    last_intent = get_last_intent(user_id)
    if last_intent:
        for intent in intents["intents"]:
            if intent["tag"] == last_intent:
                followup = intent.get("followup", {})
                if user_input.lower() in followup:
                    next_tag = followup[user_input.lower()]
                    return respond_with_intent(
                        next_tag, user_id, user_input, lat, lng
                    )
                break

    # 2. Predict intent normally
    X = vectorizer.transform([user_input])
    predicted_tag = model.predict(X)[0]

    return respond_with_intent(predicted_tag, user_id, user_input, lat, lng)


def respond_with_intent(
        tag: str, user_id: str,
        user_input: str, lat=None, lng=None):
    response_data = {"response": "", "suggestions": []}

    if tag in INTENT_REGISTRY:
        handler = INTENT_REGISTRY[tag]

        # Inspect handler parameters
        sig = inspect.signature(handler)
        params = sig.parameters

        kwargs = {}
        if "lat" in params and "lng" in params:
            kwargs["lat"] = lat
            kwargs["lng"] = lng
        
        print("user_id", user_id)

        # ✅ Pass actual user input
        response_data["response"] = handler(user_input, **kwargs)
        return response_data

    # fallback to static intents.json
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            response_data["response"] = random.choice(intent["responses"])
            response_data["suggestions"] = intent.get("suggestions", [])
            if "followup" in intent:
                set_last_intent(user_id, tag)
            else:
                clear_last_intent(user_id)
            return response_data

    return {"response": "Sorry, I didn't understand that.", "suggestions": []}



