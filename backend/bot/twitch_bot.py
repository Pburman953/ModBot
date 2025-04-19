from backend.models.lstm_model import BI_lstm_GloVe_model
from backend.utils.predict import predict_labels
from backend.utils.preprocess import preprocess
from backend import config

import socket, torch, json, numpy as np

# Load word_to_index and embeddings
with open(config.WORD_TO_INDEX_PATH) as f:
    word_to_index = json.load(f)
embedding_matrix = np.load(config.EMBEDDING_MATRIX_PATH)

# Load model
vocab_size, embed_dim = embedding_matrix.shape
model = BI_lstm_GloVe_model(vocab_size, embed_dim, config.HIDDEN_DIM, word_to_index["<pad>"], 6)
model.load_state_dict(torch.load(config.MODEL_PATH, map_location="cpu"))
model.embedding.weight.data.copy_(torch.tensor(embedding_matrix))
model.embedding.weight.requires_grad = False
model.eval()

# IRC Bot Setup
sock = socket.socket()
sock.connect((config.HOST, config.PORT))
sock.send(f"PASS {config.TOKEN}\n".encode("utf-8"))
sock.send(f"NICK {config.NICK}\n".encode("utf-8"))
sock.send(f"JOIN {config.CHANNEL}\n".encode("utf-8"))

print("Bot is running...")

while True:
    resp = sock.recv(2048).decode("utf-8")
    if resp.startswith("PING"):
        sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        continue

    if "PRIVMSG" in resp:
        username = resp.split("!")[0][1:]
        message = resp.split("PRIVMSG")[1].split(":", 1)[1].strip()

        print(f"{username}: {message}")
        results = predict_labels(message, model)
        toxic_labels = [label for label, data in results.items() if data["predicted"] == 1]

        if toxic_labels:
            warning = f"/me ⚠️ @{username}, your message may contain: {', '.join(toxic_labels)}"
            sock.send(f"PRIVMSG {config.CHANNEL} :{warning}\n".encode("utf-8"))
