import requests

SUBREDDITS = [
    "worldnews",
    "europe",
    "EuropeanUnion",
    "economics",
    "finance",
    "geopolitics",
    "Germany",
    "ukraine"
]

KEYWORDS = [
    "germany",
    "berlin",
    "eu",
    "europe",
    "european union",
    "ukraine",
    "ukrainian",
    "refugee",
    "migration",
    "economy",
    "inflation",
    "sanctions",
    "gas",
    "energy"
]


def is_relevant(title):
    title = title.lower()
    for k in KEYWORDS:
        if k in title:
            return True
    return False


def get_reddit_news():
    news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://yourdomain.com/bot)"
    }

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=30"
        try:
            res = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            print(f"Ошибка запроса к Reddit /r/{sub}: {e}")
            continue

        if res.status_code != 200:
            print(f"Ошибка запроса Reddit /r/{sub}: статус {res.status_code}")
            print("Текст ответа:", res.text[:200])
            continue

        try:
            data = res.json()
        except ValueError:
            print(f"Ошибка: ответ Reddit /r/{sub} не является JSON")
            print("Текст ответа:", res.text[:200])
            continue

        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            title = p.get("title", "")

            if not title or not is_relevant(title):
                continue
            if p.get("score", 0) < 1500:
                continue
            if p.get("num_comments", 0) < 200:
                continue

            news.append({
                "title": title,
                "link": "https://reddit.com" + p.get("permalink", ""),
                "summary": p.get("selftext", "")
            })

    return news