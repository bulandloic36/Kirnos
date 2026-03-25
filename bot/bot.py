from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os
from datetime import datetime

# ===== CONFIG =====
USERNAME = "loic_1110"  # ⚠️ SANS @

client = TikTokLiveClient(unique_id=USERNAME)

# ===== MOTS INTERDITS =====
bad_words = ["pute", "fdp", "connard", "salope", "encule"]

# ===== BAN LIST =====
banned_users = []

# ===== DOSSIER LOG =====
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/live_logs.txt"

# ===== LOG =====
def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ===== EVENT COMMENT =====
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    username = event.user.nickname
    message = event.comment.lower()

    time = datetime.now().strftime("%H:%M:%S")

    # ===== BASE =====
    log = f"[{time}] {username}: {message}"

    # ===== INSULTE =====
    if any(word in message for word in bad_words):

        log = f"[INSULTE] [{time}] {username}: {message}"

        # 👉 BAN AUTO
        banned_users.append(username)
        log += " 🚫 BANNI"

    # ===== SPAM =====
    elif message.count(" ") < 1 and len(message) > 15:
        log = f"[ALERTE] [{time}] Spam suspect: {username}"

    # ===== USER DEJA BANNI =====
    if username in banned_users:
        log = f"[BLOQUÉ] [{time}] {username} ignoré"

    print(log)
    write_log(log)

# ===== START =====
print(f"🔥 Bot connecté à @{USERNAME}")
client.run()