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
        base_path = os.path.dirname(__file__) + "/../ml/"

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

    if predicted_tag in INTENT_REGISTRY:
        handler = INTENT_REGISTRY[predicted_tag]
        return handler(user_input)

    for intent in intents["intents"]:
        if intent["tag"] == predicted_tag:
            return random.choice(intent["responses"])

    return "Sorry, I didn't understand that. Can you rephrase?"
