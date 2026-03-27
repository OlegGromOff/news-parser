import feedparser
import requests
import time
from datetime import datetime
from reddit_source import get_reddit_news
from google_news import get_google_news
from viral_ranker import rank_news
from trends_source import get_trends_news
from youtube_trends import get_youtube_trends
from openai import OpenAI
from rss_sources import RSS_FEEDS
from script_generator import generate_script
import os

# =========================
# ENV VARIABLES
# =========================
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not NOTION_TOKEN or not DATABASE_ID or not OPENAI_API_KEY:
    raise ValueError("❌ Не заданы переменные окружения (Secrets)")

# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# RSS NEWS
# =========================
def get_rss_news():
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in RSS_FEEDS:
        try:
            print("Читаем RSS:", url)
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            print("Статей:", len(feed.entries))

            for entry in feed.entries[:5]:
                news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")
                })
        except Exception as e:
            print("Ошибка RSS:", e)

    return news

# =========================
# CHECK IN NOTION
# =========================
def is_news_exists(title):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "filter": {
            "property": "Title",
            "title": {"equals": title}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        results = response.json().get("results", [])
        return len(results) > 0
    except Exception as e:
        print("Ошибка проверки Notion:", e)
        return False

# =========================
# SAVE TO NOTION
# =========================
def save_to_notion(title, script, link):
    if is_news_exists(title):
        print("Уже есть:", title)
        return

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "Script": {"rich_text": [{"text": {"content": script[:1900]}}]},
            "Source": {"url": link},
            "Status": {"select": {"name": "Script ready"}}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            print("✅ Сохранено:", title)
        else:
            print("❌ Ошибка Notion:", response.text)

    except Exception as e:
        print("Ошибка отправки в Notion:", e)

# =========================
# MAIN LOGIC
# =========================
def main():
    print(f"\n🚀 Запуск: {datetime.now()}\n")

    # Источники
    rss_news = get_rss_news()
    reddit_news = get_reddit_news()
    google_news = get_google_news()
    youtube_news = get_youtube_trends()

    try:
        trends_news = get_trends_news()
    except Exception as e:
        print("Ошибка Google Trends:", e)
        trends_news = []

    # Объединяем
    news = rss_news + reddit_news + google_news + trends_news + youtube_news
    print("Всего новостей:", len(news))

    if not news:
        print("❌ Нет новостей")
        return

    # Удаляем дубликаты
    unique_news = []
    titles = set()

    for n in news:
        if n["title"] not in titles:
            unique_news.append(n)
            titles.add(n["title"])

    news = unique_news[:60]
    print("После фильтрации:", len(news))

    # Ранжирование
    try:
        viral_ids = rank_news(news)
    except Exception as e:
        print("Ошибка ранжирования:", e)
        return

    news_to_process = []

    for i in viral_ids:
        if 0 < i <= len(news):
            news_to_process.append(news[i - 1])

    print("Будет обработано:", len(news_to_process))

    # Обработка
    for n in news_to_process:
        try:
            print("\nГенерация:", n["title"])

            summary = n.get("summary", "")
            script = generate_script(n["title"], summary)

            save_to_notion(
                n["title"],
                script,
                n.get("link", "")
            )

            time.sleep(1)  # защита от rate limits

        except Exception as e:
            print("Ошибка обработки новости:", e)

    print("\n✅ Готово\n")

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()