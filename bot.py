from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os

# ===== TON PSEUDO TIKTOK =====
USERNAME = "loic_1110"   # 🔥 remplace par ton vrai pseudo si besoin

client = TikTokLiveClient(unique_id=USERNAME)

# ===== MOTS INTERDITS =====
bad_words = ["pute", "fdp", "connard", "salope", "encule"]

# ===== DOSSIER LOG =====
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/live_logs.txt"

# ===== ECRIRE LOG =====
def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ===== EVENEMENT COMMENT =====
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    username = event.user.nickname
    message = event.comment.lower()

    # LOG NORMAL
    log = f"{username}: {message}"

    # DETECTION INSULTE
    if any(word in message for word in bad_words):
        log = f"[INSULTE] {username}: {message}"

    # DETECTION SPAM
    elif len(message) > 20 and message.count(" ") < 1:
        log = f"[ALERTE] Spam suspect: {username}"

    print(log)
    write_log(log)

# ===== LANCEMENT =====
print("🔥 Bot TikTok lancé...")
client.run()