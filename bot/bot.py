from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent

# 👉 mets ton pseudo TikTok ici
client = TikTokLiveClient(unique_id="loic_1110")

bad_words = ["pute", "fdp", "connard", "sale"]

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    message = event.comment.lower()

    print(f"{event.user.nickname}: {message}")

    # détection insultes
    if any(word in message for word in bad_words):
        print("⚠️ Insulte détectée !")

        # écrire dans un fichier pour le dashboard
        with open("data/live_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"[INSULTE] {event.user.nickname}: {message}\n")
    else:
        with open("data/live_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"{event.user.nickname}: {message}\n")

client.run()