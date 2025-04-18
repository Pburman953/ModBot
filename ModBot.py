import re
import torch
import torch.nn as nn
import numpy as np
import json
import nltk
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')
nltk.download('stopwords')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ------------ Model ------------
class BI_lstm_GloVe_model(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, pad_idx, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, text, lengths):
        embedded = self.embedding(text)
        packed_embedded = nn.utils.rnn.pack_padded_sequence(
            embedded, lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        packed_output, (hidden, cell) = self.lstm(packed_embedded)
        hidden_output = torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1)
        out = self.fc(hidden_output)
        return torch.sigmoid(out)

# ------------ Load Stuff ------------
# Load word_to_index
with open("word_to_index.json") as f:
    word_to_index = json.load(f)

# Load GloVe embeddings
embedding_matrix = np.load("glove_embeddings.npy")

# Model settings
vocab_size, embed_dim = embedding_matrix.shape
hidden_dim = 256
output_dim = 6
pad_idx = word_to_index.get("<pad>", 0)
PAD_IDX = word_to_index["<pad>"]
UNK_IDX = word_to_index["<unk>"]

# Init model
model = BI_lstm_GloVe_model(vocab_size, embed_dim, hidden_dim, pad_idx, output_dim)
model.load_state_dict(torch.load("bi_lstm_glove.pth", map_location=torch.device("cpu")))
model.embedding.weight.data.copy_(torch.tensor(embedding_matrix))
model.embedding.weight.requires_grad = False
model.eval()

# ------------ Preprocessing ------------

punc = string.punctuation
punc.replace('#', '')
punc.replace('!', '')
punc.replace('?', '')
punc = punc + "∞θ÷α•à−β∅³π‘₹´°£€\×™√²—"

chat_words = {
    "AFAIK": "As Far As I Know",
    "AFK": "Away From Keyboard",
    "ASAP": "As Soon As Possible",
    "ATK": "At The Keyboard",
    "ATM": "At The Moment",
    "A3": "Anytime, Anywhere, Anyplace",
    "BAK": "Back At Keyboard",
    "BBL": "Be Back Later",
    "BBS": "Be Back Soon",
    "BFN": "Bye For Now",
    "B4N": "Bye For Now",
    "BRB": "Be Right Back",
    "BRT": "Be Right There",
    "BTW": "By The Way",
    "B4": "Before",
    "B4N": "Bye For Now",
    "CU": "See You",
    "CUL8R": "See You Later",
    "CYA": "See You",
    "FAQ": "Frequently Asked Questions",
    "FC": "Fingers Crossed",
    "FWIW": "For What It's Worth",
    "FYI": "For Your Information",
    "GAL": "Get A Life",
    "GG": "Good Game",
    "GN": "Good Night",
    "GMTA": "Great Minds Think Alike",
    "GR8": "Great!",
    "G9": "Genius",
    "IC": "I See",
    "ICQ": "I Seek you (also a chat program)",
    "ILU": "ILU: I Love You",
    "IMHO": "In My Honest/Humble Opinion",
    "IMO": "In My Opinion",
    "IOW": "In Other Words",
    "IRL": "In Real Life",
    "KISS": "Keep It Simple, Stupid",
    "LDR": "Long Distance Relationship",
    "LMAO": "Laugh My A.. Off",
    "LOL": "Laughing Out Loud",
    "LTNS": "Long Time No See",
    "L8R": "Later",
    "MTE": "My Thoughts Exactly",
    "M8": "Mate",
    "NRN": "No Reply Necessary",
    "OIC": "Oh I See",
    "PITA": "Pain In The A..",
    "PRT": "Party",
    "PRW": "Parents Are Watching",
    "QPSA?": "Que Pasa?",
    "ROFL": "Rolling On The Floor Laughing",
    "ROFLOL": "Rolling On The Floor Laughing Out Loud",
    "ROTFLMAO": "Rolling On The Floor Laughing My A.. Off",
    "SK8": "Skate",
    "STATS": "Your sex and age",
    "ASL": "Age, Sex, Location",
    "THX": "Thank You",
    "TTFN": "Ta-Ta For Now!",
    "TTYL": "Talk To You Later",
    "U": "You",
    "U2": "You Too",
    "U4E": "Yours For Ever",
    "WB": "Welcome Back",
    "WTF": "What The F...",
    "WTG": "Way To Go!",
    "WUF": "Where Are You From?",
    "W8": "Wait...",
    "7K": "Sick:-D Laugher",
    "TFW": "That feeling when",
    "MFW": "My face when",
    "MRW": "My reaction when",
    "IFYP": "I feel your pain",
    "TNTL": "Trying not to laugh",
    "JK": "Just kidding",
    "IDC": "I don't care",
    "ILY": "I love you",
    "IMU": "I miss you",
    "ADIH": "Another day in hell",
    "ZZZ": "Sleeping, bored, tired",
    "WYWH": "Wish you were here",
    "TIME": "Tears in my eyes",
    "BAE": "Before anyone else",
    "FIMH": "Forever in my heart",
    "BSAAW": "Big smile and a wink",
    "BWL": "Bursting with laughter",
    "BFF": "Best friends forever",
    "CSL": "Can't stop laughing"
}


stpwds = stopwords.words('english')


time_zone_abbreviations = [
        "UTC", "GMT", "EST", "CST", "PST", "MST",
        "EDT", "CDT", "PDT", "MDT", "CET", "EET",
        "WET", "AEST", "ACST", "AWST", "HST",
        "AKST", "IST", "JST", "KST", "NZST"
    ]

patterns = [
    r'\\[nrtbfv\\]',         # \n, \t ..etc
    '<.*?>',                 # Html tags
    r'https?://\S+|www\.\S+',# Links
    r'\ufeff',               # BOM characters
    r'^[^a-zA-Z0-9]+$',      # Non-alphanumeric tokens
    r'ｗｗｗ．\S+',            # Full-width URLs
    r'[\uf700-\uf7ff]',      # Unicode private-use chars
    r'^[－—…]+$',            # Special punctuation-only tokens
    r'[︵︶]'                # CJK parentheses
]

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["                         # Start of group
        "\U0001F600-\U0001F64F"     # Emoticons
        "\U0001F300-\U0001F5FF"     # Symbols & pictographs
        "\U0001F680-\U0001F6FF"     # Transport & map symbols
        "\U0001F1E0-\U0001F1FF"     # Flags
        "\U00002700-\U000027BF"     # Dingbats
        "\U000024C2-\U0001F251"     # Enclosed characters
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


def preprocess(text):
    for regex in patterns:
        text = re.sub(regex, '', text)
    text = text.translate(str.maketrans(punc, ' ' * len(punc)))
    text = ' '.join(word for word in text.split() if word not in time_zone_abbreviations)
    text = ' '.join(word for word in text.split() if word not in stpwds)
    text = ' '.join(chat_words.get(word.lower(), word) for word in text.split())
    text = text.lower()
    text = remove_emojis(text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ------------ Prediction Function ------------
def predict_labels(text, model):
    tokens = word_tokenize(preprocess(text))
    numericalized = [word_to_index.get(token, UNK_IDX) for token in tokens]
    text_tensor = torch.tensor([numericalized], dtype=torch.long).to(device)
    lengths = torch.tensor([len(numericalized)], dtype=torch.long).to(device)

    with torch.no_grad():
        output = model(text_tensor, lengths)

    probabilities = output.squeeze().cpu().numpy()
    predicted_labels = (probabilities > 0.5).astype(int)

    label_names = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    results = {}
    for i in range(len(label_names)):
        results[label_names[i]] = {
            "probability": float(probabilities[i]),
            "predicted": int(predicted_labels[i])
        }
    return results


# ------------ For testing ------------
if __name__ == "__main__":
    user_input = input("Enter text: ")

    # Make prediction
    predictions = predict_labels(user_input, model)

    # Print results
    for label, result in predictions.items():
        print(f"{label}: Probability = {result['probability']:.4f}, Predicted = {result['predicted']}")