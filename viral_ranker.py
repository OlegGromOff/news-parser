from openai import OpenAI
import os  # <-- импортируем os для env переменных

# Получаем ключ OpenAI из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ Не задана переменная окружения OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def rank_news(news):

    news_list = ""

    for i, n in enumerate(news):
        news_list += f"{i+1}. {n['title']}\n"

    prompt = f"""
Ты редактор вирусных новостей для TikTok и Shorts.

Оцени каждую новость по шкале 1-10 по следующим критериям:

- скандал
- деньги
- новые законы
- миграция
- Украина
- Германия
- социальная несправедливость
- кризис

Новости:

{news_list}

Верни только 5 номеров новостей с самым высоким вирусным потенциалом.

Формат ответа:

1 5 9 12 14
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    ids = [int(x) for x in result.split()]

    return ids