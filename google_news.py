import feedparser
import urllib.parse

TOPICS = [
    "Germany economy",
    "Germany refugees",
    "Germany migrants",
    "EU economy",
    "European Union sanctions",
    "Ukraine war",
    "Ukrainians in Europe",
    "Ukrainian refugees Europe",
    "inflation Europe",
    "gas prices Europe"
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