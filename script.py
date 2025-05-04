import os
import requests
from datetime import datetime, timedelta, timezone
from telegram import Bot

# --- CONFIGURATION ---
API_KEY   = os.environ["CRYPTOPANIC_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]

URL = "https://cryptopanic.com/api/v1/posts/"
bot = Bot(token=BOT_TOKEN)

def fetch_major_news():
    params = {
        "auth_token": API_KEY,
        "public": "true",
        "filter": "important",
        "kind": "news"
    }
    r = requests.get(URL, params=params)
    r.raise_for_status()
    return r.json().get("results", [])

def send_to_telegram(title, url, source, published_at):
    text = (
        f"*{title}*\n"
        f"Source : {source}\n"
        f"Publiée à {published_at.strftime('%H:%M le %d/%m/%Y UTC')}\n"
        f"{url}"
    )
    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

def main():
    now = datetime.now(timezone.utc)
    window = now - timedelta(minutes=6)
    for post in fetch_major_news():
        pub = datetime.fromisoformat(post["published_at"].replace("Z", "+00:00"))
        if pub < window:
            continue
        send_to_telegram(
            title=post["title"],
            url=post["url"],
            source=post["source"]["title"],
            published_at=pub
        )

if __name__ == "__main__":
    main()
