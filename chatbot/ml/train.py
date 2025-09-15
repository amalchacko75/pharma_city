import json
# import random
import nltk
# import numpy as np
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

nltk.download("punkt")

# Load intents
with open("chatbot/ml/intents.json") as f:
    data = json.load(f)

# Prepare training data
sentences = []
labels = []
classes = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        sentences.append(pattern)
        labels.append(intent["tag"])
    if intent["tag"] not in classes:
        classes.append(intent["tag"])

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(sentences)
y = labels

# Train model
model = MultinomialNB()
model.fit(X, y)

# Save model & vectorizer
pickle.dump(model, open("chatbot/ml/model.pkl", "wb"))
pickle.dump(vectorizer, open("chatbot/ml/vectorizer.pkl", "wb"))
pickle.dump(classes, open("chatbot/ml/classes.pkl", "wb"))
