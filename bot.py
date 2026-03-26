from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os
import re

# ===== CONFIG =====
USERNAME = "TON_PSEUDO"

client = TikTokLiveClient(unique_id=USERNAME)

# ===== DOSSIER =====
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/live_logs.txt"

# ===== LISTE INSULTES =====
bad_words = [
    "pute", "fdp", "connard", "salope", "encule",
    "batard", "ntm", "tg", "nique"
]

# ===== NORMALISATION TEXTE =====
def normalize(text):
    text = text.lower()

    # remplace lettres stylées
    text = text.replace("@", "a").replace("4", "a")
    text = text.replace("0", "o").replace("1", "i")
    text = text.replace("3", "e")

    # supprime caractères spéciaux
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    return text

# ===== IA DETECTION =====
def detect_toxic(message):

    msg = normalize(message)

    score = 0

    # insultes directes
    for word in bad_words:
        if word in msg:
            score += 2

    # spam (message trop long sans espace)
    if len(msg) > 20 and " " not in msg:
        score += 1

    # répétition lettres
    if re.search(r"(.)\1{5,}", msg):
        score += 1

    # MAJUSCULE SPAM
    if message.isupper() and len(message) > 10:
        score += 1

    # classification
    if score >= 2:
        return "INSULTE"
    elif score == 1:
        return "ALERTE"
    else:
        return "OK"

# ===== LOG =====
def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# ===== EVENT =====
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    user = event.user.nickname
    message = event.comment

    result = detect_toxic(message)

    if result == "INSULTE":
        log = f"[INSULTE] {user}: {message}"

        # 🔥 BAN AUTO (simulation)
        log += " → BAN"

    elif result == "ALERTE":
        log = f"[ALERTE] {user}: {message}"

    else:
        log = f"{user}: {message}"

    print(log)
    write_log(log)

    # ===== START =====
print("🔥 IA BOT ACTIVÉ")
client.run()