import feedparser
import requests
import json
import time
from datetime import datetime
from reddit_source import get_reddit_news
from google_news import get_google_news
from viral_ranker import rank_news
from trends_source import get_trends_news
from youtube_trends import get_youtube_trends
from openai import OpenAI
from rss_sources import RSS_FEEDS
# from config import NOTION_TOKEN, DATABASE_ID
from script_generator import generate_script
# from config import OPENAI_API_KEY

import os

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Файл для хранения уже обработанных новостей
PROCESSED_FILE = "processed_news.json"

# Загружаем уже обработанные новости
try:
    with open(PROCESSED_FILE, "r") as f:
        processed_news = json.load(f)
except FileNotFoundError:
    processed_news = []

def save_processed_news():
    with open(PROCESSED_FILE, "w") as f:
        json.dump(processed_news, f, indent=2)

def translate_to_russian(text):
    """
    Переводит текст на русский язык, сохраняя цифры, даты и названия
    """
    prompt = f"Переведи текст на русский язык, сохрани все цифры, даты и названия:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def get_rss_news():
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in RSS_FEEDS:
        print("Читаем RSS:", url)
        response = requests.get(url, headers=headers)
        feed = feedparser.parse(response.content)
        print("Статей:", len(feed.entries))

        for entry in feed.entries[:5]:
            news_id = entry.get("id") or entry.get("link")
            if news_id in processed_news:
                continue  # уже обработано
            news.append({
                "id": news_id,
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", "")
            })
    return news

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
    response = requests.post(url, headers=headers, json=data)
    results = response.json().get("results")
    return len(results) > 0

def save_to_notion(title, script, link):
    if is_news_exists(title):
        print("Новость уже есть:", title)
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
    response = requests.post(url, headers=headers, json=data)
    print("Notion status:", response.status_code)

def main():
    print(f"Запуск скрипта: {datetime.now()}")

    # Получаем все новости
    rss_news = get_rss_news()
    reddit_news = get_reddit_news()
    google_news = get_google_news()
    youtube_news = get_youtube_trends()
    try:
        trends_news = get_trends_news()
    except Exception as e:
        print("Ошибка Google Trends:", e)
        trends_news = []

    news = rss_news + reddit_news + google_news + trends_news + youtube_news
    print("Всего новых новостей:", len(news))

    if not news:
        print("Нет новых новостей")
        return

    # Удаляем дубликаты по заголовку
    unique_news = []
    titles = set()
    for n in news:
        if n["title"] not in titles:
            unique_news.append(n)
            titles.add(n["title"])
    news = unique_news[:60]

    print("После удаления дублей:", len(news))

    # AI выбирает вирусные
    viral_ids = rank_news(news)
    news_to_process = []
    for i in viral_ids:
        if 0 < i <= len(news):
            news_to_process.append(news[i-1])

    print("Будет создано сценариев:", len(news_to_process))

    for n in news_to_process:
        print("Генерируем:", n["title"])

        summary = n.get("summary", "")

        script = generate_script(n["title"], summary)
        title_ru = n["title"]
        save_to_notion(title_ru, script, n.get("link", ""))

        # Ставим уникальный ID для кеша
        # Если есть id — берем его, иначе используем link, иначе title+summary
        news_id = n.get("id") or n.get("link") or (n["title"] + summary)
        processed_news.append(news_id)

    save_processed_news()
    print("Обработка завершена.")

# if __name__ == "__main__":
#     while True:
#         main()
#         print("Ожидание 10 часов до следующего запуска...")
#         time.sleep(10 * 60 * 60)  # 10 часов

if __name__ == "__main__":
    main()