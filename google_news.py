import feedparser
import urllib.parse

TOPICS = [
    "Germany economy",
    "Berlin startups",
    "Germany jobs",
    "EU tech",
    "AI Europe",
    "housing Berlin",
    "cost of living Germany",
    "inflation Germany",
    "digital Germany",
    "Ukrainians in Europe",
    "remote work Europe"
]

def get_google_news():

    news = []

    for topic in TOPICS:

        query = urllib.parse.quote(topic)

        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

        print("Google News:", topic)

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:

            news.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", "")
            })

    return news