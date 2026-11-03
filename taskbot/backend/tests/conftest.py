# Конфигурация тестового окружения: pytest импортирует conftest.py до
# тестовых модулей, поэтому переменные, обязательные при импорте app.main,
# задаются ЗДЕСЬ, до первого `from app.main import app`.

import os

# app.main падает с RuntimeError на импорте без BOT_SECRET (мутации API
# нечем аутентифицировать). В тестах подставляем фиктивное значение:
# setdefault не перезатрёт переменную, если она уже задана в окружении.
os.environ.setdefault("BOT_SECRET", "test-secret-for-ci")
