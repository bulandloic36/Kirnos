from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os
import time

# ===== CONFIG =====
USERNAME = "TON_PSEUDO"

client = TikTokLiveClient(unique_id=USERNAME)

# ===== DATA =====
bad_words = ["pute", "fdp", "connard", "salope", "encule"]
user_messages = {}
banned_users = set()

# ===== DOSSIER LOG =====
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/live_logs.txt"

def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ===== BAN =====
async def ban_user(user):
    if user in banned_users:
        return

    banned_users.add(user)

    log = f"[BAN] {user} a été banni"
    print(log)
    write_log(log)

    # ⚠️ TikTok API ban réel pas dispo facilement
    # donc on simule (dashboard + blocage logique)

# ===== EVENT =====
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    username = event.user.nickname
    message = event.comment.lower()

    # ignore si déjà banni
    if username in banned_users:
        return

    now = time.time()

    # ===== SPAM SYSTEM =====
    if username not in user_messages:
        user_messages[username] = []

    user_messages[username].append(now)

    # garder seulement les 5 dernières secondes
    user_messages[username] = [
        t for t in user_messages[username] if now - t < 5
    ]

    # ===== DETECTION =====

    # INSULTE
    if any(word in message for word in bad_words):
        log = f"[INSULTE] {username}: {message}"
        print(log)
        write_log(log)

        await ban_user(username)
        return

    # SPAM (5 messages en 5 sec)
    if len(user_messages[username]) > 5:
        log = f"[ALERTE] Spam détecté: {username}"
        print(log)
        write_log(log)

        await ban_user(username)
        return

    # NORMAL
    log = f"{username}: {message}"
    print(log)
    write_log(log)

# ===== START =====
print("🔥 BOT PRO MAX ACTIF")
client.run()