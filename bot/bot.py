from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent

# 👉 mets ton pseudo TikTok ici
client = TikTokLiveClient(unique_id="loic_1110")

bad_words = ["pute", "fdp", "connard", "sale"]

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):

    message = event.comment.lower()
    username = event.user.nickname

    # LOG PAR DÉFAUT
    log = f"{username}: {message}"

    # DÉTECTION INSULTES
    if any(word in message for word in bad_words):
        log = f"[INSULTE] {username}: {message}"

    print(log)

    # UNE SEULE ÉCRITURE
    with open("data/live_logs.txt", "a", encoding="utf-8") as f:
        f.write(log + "\n")
client.run()