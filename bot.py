from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import os
import sys

username = sys.argv[1]  # 🔥 récupère pseudo depuis le site

bad_words = ["pute", "fdp", "connard", "salope"]

log_file = f"data/{username}.txt"

os.makedirs("data", exist_ok=True)

client = TikTokLiveClient(unique_id=username)

def write_log(text):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    user = event.user.nickname
    message = event.comment.lower()

    if any(word in message for word in bad_words):
        log = f"[INSULTE] {user}: {message}"
    else:
        log = f"{user}: {message}"

    print(log)
    write_log(log)

print(f"🔥 Bot lancé pour {username}")
client.run()