import os
import random
import pickle
import json

from chatbot.registry import INTENT_REGISTRY
import chatbot.handlers  # noqa: F401

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


def get_response(user_input: str):
    load_artifacts()

    X = vectorizer.transform([user_input])
    predicted_tag = model.predict(X)[0]

    print("Predicted tag:", predicted_tag)
    print("Registry now has:", INTENT_REGISTRY)

    response_data = {"response": "", "suggestions": []}

    # Case 1: Handler-based response
    if predicted_tag in INTENT_REGISTRY:
        handler = INTENT_REGISTRY[predicted_tag]
        response_data["response"] = handler(user_input)

        # add next-step suggestions from intents.json
        for intent in intents["intents"]:
            if intent["tag"] == predicted_tag:
                response_data["suggestions"] = intent.get("suggestions", [])
                break
        return response_data

    # Case 2: Static intents.json response
    for intent in intents["intents"]:
        if intent["tag"] == predicted_tag:
            response_data["response"] = random.choice(intent["responses"])
            response_data["suggestions"] = intent.get("suggestions", [])
            return response_data

    # Case 3: fallback
    return {
        "response": "Sorry, I didn't understand that. Can you rephrase?",
        "suggestions": []
    }
