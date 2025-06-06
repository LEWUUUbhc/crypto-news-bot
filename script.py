import os
import asyncio
import feedparser
from datetime import datetime, timedelta, timezone
from telegram import Bot
from telegram.helpers import escape_markdown

print("ENV:", {
    "BOT_TOKEN": "TELEGRAM_TOKEN" in os.environ,
    "CHAT_ID":   "CHAT_ID" in os.environ
})

# --- CONFIGURATION ---
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]

FEED_URLS = [
    "https://www.theblockcrypto.com/rss",
    "https://decrypt.co/feed",
    "https://cryptobriefing.com/feed/",
]
bot = Bot(token=BOT_TOKEN)

def fetch_major_news():
    for url in FEED_URLS:
        feed = feedparser.parse(url)
        source = feed.feed.get("title", url)
        for entry in feed.entries:
            # try published_parsed then updated_parsed
            t = entry.get("published_parsed") or entry.get("updated_parsed")
            if not t:
                continue
            pub_date = datetime(*t[:6], tzinfo=timezone.utc)
            yield {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "source": source,
                "published_at": pub_date,
            }

async def send_to_telegram(title, url, source, published_at):
    safe_title = escape_markdown(title, version=2)
    safe_source = escape_markdown(source, version=2)
    text = (
        f"*{safe_title}*\n"
        f"Source : {safe_source}\n"
        f"Publiée à {published_at.strftime('%H:%M le %d/%m/%Y UTC')}\n"
        f"{url}"
    )
    # ton message de debug
    print("Posting:", title, published_at.isoformat(), url)
    # **bien indenté** dans la fonction
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="MarkdownV2")

async def main():
    now = datetime.now(timezone.utc)
    window = now - timedelta(minutes=6)
    for post in fetch_major_news():
        pub = post["published_at"]
        if pub < window:
            continue
        await send_to_telegram(
            title=post["title"],
            url=post["url"],
            source=post["source"],
            published_at=pub,
        )

if __name__ == "__main__":
    asyncio.run(main())
