from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os
import time

# ===== CONFIG =====
USERNAME = "kirnos24"  # 🔥 ton TikTok
SAFE_MODE = True       # 🔒 mode sécurisé activé

client = TikTokLiveClient(unique_id=USERNAME)

# ===== DATA =====
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/live_logs.txt"

bad_words = ["pute", "fdp", "connard", "salope", "encule"]

user_messages = {}  # anti spam tracking

# ===== LOG =====
def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ===== DETECTION INTELLIGENTE =====
def is_insult(message):
    msg = message.lower()

    for word in bad_words:
        if word in msg:
            return True
    return False

def is_spam(username, message):
    now = time.time()

    if username not in user_messages:
        user_messages[username] = []

    user_messages[username].append(now)

    # garder seulement 5 dernières secondes
    user_messages[username] = [
        t for t in user_messages[username] if now - t < 5
    ]

    # spam si +5 messages en 5 sec
    if len(user_messages[username]) > 5:
        return True

    # message suspect (genre "AAAAAAAAAAAA")
    if len(message) > 15 and message.count(" ") < 1:
        return True

    return False

# ===== EVENT =====
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    username = event.user.nickname
    message = event.comment.strip()

    # ===== INSULTE =====
    if is_insult(message):
        log = f"[INSULTE] {username}: {message}"

        if SAFE_MODE:
            log += " (SAFE)"
        else:
            log += " (BAN)"

    # ===== SPAM =====
    elif is_spam(username, message):
        log = f"[ALERTE] Spam détecté: {username}"

    # ===== NORMAL =====
    else:
        log = f"{username}: {message}"

    print(log)
    write_log(log)

# ===== START =====
print("🔥 Kirnos Bot SAFE MODE PRO lancé")
client.run()