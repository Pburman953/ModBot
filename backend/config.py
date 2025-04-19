# Twitch IRC config
HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = "ModBot3000_pb"
TOKEN = "oauth:jss6sf07xzpdv1sfn14qwgosl98akh"
CHANNEL = "#cawgo953"

# Model paths
MODEL_PATH = "backend/models/bi_lstm_glove.pth"
EMBEDDING_MATRIX_PATH = "backend/models/glove_embeddings.npy"
WORD_TO_INDEX_PATH = "backend/models/word_to_index.json"
OFFENSES_FILE = "backend/bot/user_offenses.json"
# Model hyperparams
HIDDEN_DIM = 256