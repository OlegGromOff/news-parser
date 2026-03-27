import feedparser

def get_youtube_trends():

    url = "https://www.youtube.com/feeds/videos.xml?chart=mostPopular"

    feed = feedparser.parse(url)

    news = []

    for entry in feed.entries[:10]:

        news.append({
            "title": entry.title,
            "summary": "Trending topic on YouTube",
            "link": entry.link
        })

    return news