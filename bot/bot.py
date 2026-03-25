from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os

# ===== CONFIG =====
USERNAME = "@loic_1110"  # 🔥 mets ton pseudo TikTok ici

client = TikTokLiveClient(unique_id=USERNAME)

# ===== MOTS INTERDITS =====
bad_words = ["pute", "fdp", "connard", "salope", "encule"]

# ===== DOSSIER LOG =====
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/live_logs.txt"

# ===== FONCTION LOG =====
def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ===== EVENT COMMENT =====
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    username = event.user.nickname
    message = event.comment.lower()

    # ===== LOG NORMAL =====
    log = f"{username}: {message}"

    # ===== INSULTE =====
    if any(word in message for word in bad_words):
        log = f"[INSULTE] {username}: {message}"

    # ===== SPAM =====
    elif message.count(" ") < 1 and len(message) > 15:
        log = f"[ALERTE] Spam suspect: {username}"

    print(log)
    write_log(log)

# ===== START =====
print("🔥 Bot lancé...")
client.run()