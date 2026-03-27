from pytrends.request import TrendReq

KEYWORDS = [
    "Germany economy",
    "Germany refugees",
    "Ukraine war",
    "EU sanctions",
    "gas prices Europe",
    "inflation Germany",
    "Ukrainians in Europe"
]

def get_trends_news():

    pytrends = TrendReq(hl="en-US", tz=360)

    news = []

    for kw in KEYWORDS:

        print("Trends:", kw)

        pytrends.build_payload([kw], timeframe="now 1-d")

        related = pytrends.related_queries()

        if kw in related and related[kw]["rising"] is not None:

            for r in related[kw]["rising"].head(5).itertuples():

                news.append({
                    "title": r.query,
                    "summary": "Trending topic on Google",
                    "link": "https://trends.google.com"
                })

    return news