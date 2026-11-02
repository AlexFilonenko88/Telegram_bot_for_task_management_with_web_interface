"""Конфигурация Telegram-бота.

Секреты читаются только из окружения (файл .env подхватывается через
python-dotenv). Отсутствие обязательных переменных — ошибка запуска
(fail-fast), а не тихая работа с небезопасным значением по умолчанию.
"""

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")
BOT_SECRET = os.getenv("BOT_SECRET")

if not BOT_TOKEN:
    raise RuntimeError(
        "Переменная окружения BOT_TOKEN не задана: бот не сможет подключиться "
        "к Telegram. Укажите её в .env (см. .env.example)."
    )

if not BOT_SECRET:
    raise RuntimeError(
        "Переменная окружения BOT_SECRET не задана: API отклонит запросы бота. "
        "Укажите её в .env (см. .env.example)."
    )
