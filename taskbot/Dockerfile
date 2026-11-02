# =============================================================================
# Dockerfile для FastAPI-приложения TaskBot (production-ready)
#
# Сборка (контекст — папка taskbot/, т.к. бэкенд монтирует ../frontend/static):
#   cd taskbot
#   docker build -t taskbot-api .
# Запуск:
#   docker run -d -p 8000:8000 --env-file .env taskbot-api
#
# Используется multi-stage build:
#   Этап 1 (builder) — установка зависимостей в изолированное виртуальное
#                      окружение /opt/venv. Здесь же остаются все инструменты
#                      сборки (gcc и т.п.) — в финальный образ они не попадут.
#   Этап 2 (final)   — чистый python:3.11-slim + venv + только код приложения.
# =============================================================================

# --- Этап 1: builder — сборка зависимостей -----------------------------------

# Базовый образ сборщика. Тег -slim заметно меньше полного образа (нет doc,
# gcc и прочих "тяжёлых" пакетов), а для pip этого достаточно.
FROM python:3.11-slim AS builder

# Отключаем запись .pyc-файлов и буферизацию stdout/stderr:
# логи сразу видны в `docker logs`, образ не засоряется байткодом.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая папка этапа сборки — в финальный образ она не переносится.
WORKDIR /build

# Инструменты для компиляции пакетов, у которых нет готовых wheel-бинарей
# под Python 3.11 (большинство зависимостей ставятся wheel'ами, gcc — страховка).
# apt-кэш чистим в том же слое, чтобы он не остался в образе.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем ТОЛЬКО requirements.txt: слой зависимостей пересобирается
# лишь при изменении списка пакетов, а не при каждой правке кода (кэш слоёв).
COPY backend/requirements.txt .

# Создаём виртуальное окружение и ставим зависимости:
#   --no-cache-dir      — не хранить кэш pip (меньше размер слоя);
#   --upgrade pip       — свежий pip для корректной установки wheel'ов.
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# --- Этап 2: final — лёгкий production-образ ----------------------------------

# Новый чистый образ: в него попадает только /opt/venv из builder'а
# и код приложения. Никаких gcc, apt-кэшей и исходников зависимостей.
FROM python:3.11-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # venv из этапа builder первым в PATH: python/pip/uvicorn берутся из него.
    PATH="/opt/venv/bin:$PATH" \
    # Виртуальное окружение "пришито" по абсолютному пути /opt/venv.
    VIRTUAL_ENV=/opt/venv

# Создаём непривилегированного пользователя appuser (группа + пользователь,
# без пароля и без sudo). Запуск процесса не от root — требование безопасности:
# скомпрометированный контейнер не получает права суперпользователя.
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Каталоги приложения заранее создаём и отдаём appuser: WORKDIR и COPY создают
# каталоги от root, а SQLite пишет файл БД (tasks.db) прямо в /app/backend —
# без этого на старте получаем "unable to open database file".
# chown делаем ДО копирования содержимого: владельца файлов задаёт COPY --chown,
# так что дублирования слоёв не происходит.
RUN mkdir -p /app/backend /app/frontend \
    && chown -R appuser:appuser /app

WORKDIR /app/backend

# Забираем из builder'а только готовое виртуальное окружение с зависимостями.
COPY --from=builder /opt/venv /opt/venv

# Копируем только нужные файлы приложения (лишнее отсекает .dockerignore):
#   app/        — исходники FastAPI;
#   alembic/    — миграции (нужны, чтобы накатывать схему БД в контейнере);
#   alembic.ini — конфигурация alembic.
# --chown сразу задаёт владельца appuser:appuser — без последующего chown
# (дополнительный chown создаёт дублирующий слой и раздувает образ).
COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/alembic ./alembic
COPY --chown=appuser:appuser backend/alembic.ini ./

# Статика фронтенда и страница дашборда: приложение отдаёт их по путям
# ../frontend/static и ../frontend/index.html относительно WORKDIR,
# поэтому сохраняем ту же структуру каталогов.
COPY --chown=appuser:appuser frontend/static /app/frontend/static
COPY --chown=appuser:appuser frontend/index.html /app/frontend/index.html

# Документируем порт, который слушает uvicorn (информация для docker run -p).
EXPOSE 8000

# Переключаемся на непривилегированного пользователя — все дальнейшие
# команды (и сам процесс uvicorn) выполняются от appuser.
USER appuser

# HEALTHCHECK: Docker регулярно проверяет живость контейнера и помечает его
# healthy/unhealthy (docker ps, --filter health=status, авторестарт оркестраторами).
#   --interval     — раз в 30 секунд;
#   --timeout      — ответ должен прийти за 5 секунд;
#   --start-period — 15 секунд на запуск приложения (не считаются как фейлы);
#   --retries      — 3 неудачи подряд => статус unhealthy.
# Проверяем публичный эндпоинт "/" через urllib (curl в slim-образ не ставим,
# чтобы не увеличивать размер; urlopen бросает исключение при ошибке HTTP —
# ненулевой код выхода здоровье и фиксирует).
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)"

# Точка входа: uvicorn слушает все интерфейсы контейнера на порту 8000.
# Количество воркеров при необходимости задаётся переменной WEB_CONCURRENCY
# (uvicorn читает её автоматически).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
