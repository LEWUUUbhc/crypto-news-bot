import os
import feedparser
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from telegram import Bot

print("ENV:", {
    "BOT_TOKEN": "TELEGRAM_TOKEN" in os.environ,
    "CHAT_ID":   "CHAT_ID" in os.environ
})

# --- CONFIGURATION ---
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]

FEED_URL = "https://cointelegraph.com/rss"
bot = Bot(token=BOT_TOKEN)

def fetch_major_news():
    feed = feedparser.parse(FEED_URL)
    return feed.entries

def send_to_telegram(title, url, source, published_at):
    text = (
        f"*{title}*\n"
        f"Source : {source}\n"
        f"Publiée à {published_at.strftime('%H:%M le %d/%m/%Y UTC')}\n"
        f"{url}"
    )
    # ton message de debug
    print("Posting:", title, published_at.isoformat(), url)
    # **bien indenté** dans la fonction
    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

def main():
    now = datetime.now(timezone.utc)
    window = now - timedelta(minutes=6)
    for post in fetch_major_news():
        if hasattr(post, "published"):
            pub = parsedate_to_datetime(post.published)
        else:
            pub = now
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        else:
            pub = pub.astimezone(timezone.utc)
        if pub < window:
            continue
        send_to_telegram(
            title=post.title,
            url=post.link,
            source="Cointelegraph",
            published_at=pub
        )

if __name__ == "__main__":
    main()
