import requests

# Список сабреддитов
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

# Ключевые слова для фильтрации новостей
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

# Проверка, релевантен ли заголовок ключевым словам
def is_relevant(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS)

# Получение новостей с Reddit
def get_reddit_news(limit_per_subreddit=30, min_score=1500, min_comments=200):
    news = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0.0.0 Safari/537.36"
    }

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={limit_per_subreddit}"
        try:
            print(f"Запрашиваем Reddit /r/{sub}")
            res = requests.get(url, headers=headers, timeout=10)

            if res.status_code != 200:
                print(f"Ошибка запроса Reddit /r/{sub}: статус {res.status_code}")
                print("Текст ответа:", res.text[:200])
                continue

            data = res.json()
            for post in data.get("data", {}).get("children", []):
                p = post.get("data", {})
                title = p.get("title", "")
                if not title or not is_relevant(title):
                    continue
                if p.get("score", 0) < min_score:
                    continue
                if p.get("num_comments", 0) < min_comments:
                    continue

                news.append({
                    "title": title,
                    "link": "https://reddit.com" + p.get("permalink", ""),
                    "summary": p.get("selftext", "")
                })

        except requests.RequestException as e:
            print(f"Ошибка запроса Reddit /r/{sub}: {e}")
        except ValueError:
            print(f"Ошибка: ответ Reddit /r/{sub} не является JSON")
            print("Текст ответа:", res.text[:200])

    print(f"Собрано новостей с Reddit: {len(news)}")
    return news