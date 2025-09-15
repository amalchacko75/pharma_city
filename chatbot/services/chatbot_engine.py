import random
import pickle
import json

# Load trained model
model = pickle.load(open("chatbot/ml/model.pkl", "rb"))
vectorizer = pickle.load(open("chatbot/ml/vectorizer.pkl", "rb"))

with open("chatbot/ml/intents.json") as f:
    intents = json.load(f)


def get_response(user_input: str):
    X = vectorizer.transform([user_input])
    predicted_tag = model.predict(X)[0]

    for intent in intents["intents"]:
        if intent["tag"] == predicted_tag:
            return random.choice(intent["responses"])

    return "Sorry, I didn’t understand that. Can you rephrase?"
