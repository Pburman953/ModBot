from backend.models.lstm_model import BI_lstm_GloVe_model
from backend.utils.predict import predict_labels
from backend.utils.preprocess import preprocess
from backend import config

import socket, torch, json, numpy as np
from backend.utils.user_tracker import update_offense, get_offenses, reset_offenses
from backend.utils.adaptive_punishment2 import adaptive_punishment
from backend.utils.moderation import get_user_id, check_token_permissions  # Adjust if your path differs
from backend.utils.adaptive_punishment2 import add_to_whitelist, load_whitelist

ACCESS_TOKEN = config.ACCESS_TOKEN
CLIENT_ID = config.CLIENT_ID
MODERATOR_ID = config.MODERATOR_ID
BROADCASTER_ID = config.BROADCASTER_ID

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

# Load whitelist
load_whitelist()


def fetch_and_store_ids():
    access_token = config.ACCESS_TOKEN
    client_id = config.CLIENT_ID
    channel_name = config.CHANNEL.replace("#", "")  # Just the username
    bot_username = config.NICK

    # Get broadcaster and moderator IDs
    broadcaster_id = get_user_id(channel_name, access_token, client_id)
    moderator_id = get_user_id(bot_username, access_token, client_id)

    if not broadcaster_id or not moderator_id:
        raise Exception("❌ Failed to fetch required Twitch user IDs.")

    # Read the config.py file
    with open(config.__file__, "r") as f:
        lines = f.readlines()

    # Update or insert broadcaster_id and moderator_id
    updated_lines = []
    found_broadcaster = found_moderator = False

    for line in lines:
        if line.startswith("BROADCASTER_ID"):
            updated_lines.append(f'BROADCASTER_ID = "{broadcaster_id}"\n')
            found_broadcaster = True
        elif line.startswith("MODERATOR_ID"):
            updated_lines.append(f'MODERATOR_ID = "{moderator_id}"\n')
            found_moderator = True
        else:
            updated_lines.append(line)

    # Add if missing
    if not found_broadcaster:
        updated_lines.append(f'\nBROADCASTER_ID = "{broadcaster_id}"\n')
    if not found_moderator:
        updated_lines.append(f'\nMODERATOR_ID = "{moderator_id}"\n')

    # Write back to config.py
    with open(config.__file__, "w") as f:
        f.writelines(updated_lines)

    print("✅ Twitch IDs updated in config.py")



# IRC Bot Setup
sock = socket.socket()
sock.connect((config.HOST, config.PORT))
sock.send(f"PASS oauth:{config.ACCESS_TOKEN}\n".encode("utf-8"))
sock.send(f"NICK {config.NICK}\n".encode("utf-8"))
sock.send(f"JOIN {config.CHANNEL}\n".encode("utf-8"))

check_token_permissions(config.ACCESS_TOKEN)

print("Bot is running...")

add_to_whitelist(config.CHANNEL.replace("#", ""))

fetch_and_store_ids()

while True:
    resp = sock.recv(2048).decode("utf-8")
    if resp.startswith("PING"):
        sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        continue

    if "PRIVMSG" in resp:
        username = resp.split("!")[0][1:]
        message = resp.split("PRIVMSG")[1].split(":", 1)[1].strip()

        print(f"{username}: {message}")
        results = predict_labels(preprocess(message), model)
        toxic_labels = [label for label, data in results.items() if data["predicted"] == 1]

        if toxic_labels:
            warning = f"/me ⚠️ @{username}, your message may contain: {', '.join(toxic_labels)}"
            sock.send(f"PRIVMSG {config.CHANNEL} :{warning}\n".encode("utf-8"))

            # Use API-based punishment instead of IRC-based
            adaptive_punishment(
                username=username,
                toxicity_labels=toxic_labels,
                access_token=ACCESS_TOKEN,
                client_id=CLIENT_ID,
                moderator_id=MODERATOR_ID,
                broadcaster_id=BROADCASTER_ID
            )


