import torch
import numpy as np
from nltk.tokenize import word_tokenize
from backend.utils.preprocess import preprocess
import json

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Load word_to_index
with open('backend/models/word_to_index.json') as f:
    word_to_index = json.load(f)

PAD_IDX = word_to_index["<pad>"]
UNK_IDX = word_to_index["<unk>"]


def predict_labels(text, model, threshold):
    tokens = word_tokenize(preprocess(text))
    numericalized = [word_to_index.get(token, UNK_IDX) for token in tokens]
    text_tensor = torch.tensor([numericalized], dtype=torch.long).to(device)
    lengths = torch.tensor([len(numericalized)], dtype=torch.long).to(device)

    with torch.no_grad():
        output = model(text_tensor, lengths)

    probabilities = output.squeeze().cpu().numpy()
    predicted_labels = (probabilities > threshold).astype(int)

    label_names = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    results = {}
    for i in range(len(label_names)):
        results[label_names[i]] = {
            "probability": float(probabilities[i]),
            "predicted": int(predicted_labels[i])
        }
    return results
