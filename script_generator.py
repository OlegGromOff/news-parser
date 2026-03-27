from openai import OpenAI
import os  # <-- импортируем os для env переменных

# Получаем ключ OpenAI из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ Не задана переменная окружения OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_script(title, summary):

    prompt = f"""
Ты пишешь текст для телесуфлёра.

Это новостной рилс для блога «Одесский Берлин».

ВАЖНО:
Новость может быть на английском или немецком.
Сначала правильно пойми смысл новости,
при необходимости переведи её на русский,
а затем напиши сценарий на русском языке.

Очень важно:

Пиши как живую речь человека в камеру.

[... весь текст без изменений ...]

Новость:

Заголовок:
{title}

Описание:
{summary}

Финал всегда такой:

Пишите, что вы думаете по этому поводу.
С вами была Юлия Гром.
Блог Одесский Берлин.
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content.strip()