# TaskBot - Telegram бот для управления задачами

Telegram бот для управления задачами с веб-интерфейсом и REST API.

## Возможности

- CRUD операций с задачами через Telegram бота
- Статусы задач: активна / выполнена
- Веб-дашборд с графиком выполнения за неделю
- REST API для интеграций
- Авторизация по Telegram user_id (без регистрации и паролей)

## Архитектура

- **Единственный источник правды — база данных.** Бот и веб читают данные через один и тот же API
- **Бот — клиент API, не самостоятельный сервис.** Логика переиспользуется и тестируется через Swagger
- **FastAPI — единственная точка входа в данные.** Вся бизнес-логика живёт здесь

## Структура проекта

```
taskbot/
├── backend/                    # FastAPI приложение
│   ├── app/
│   │   ├── main.py             # Точка входа FastAPI
│   │   ├── database.py         # Подключение к БД, сессия
│   │   ├── models.py           # SQLAlchemy модели
│   │   ├── schemas/            # Pydantic схемы (валидация)
│   │   ├── crud.py             # CRUD операции с БД
│   │   └── routers/            # API роутеры
│   ├── alembic/                # Миграции базы данных
│   └── requirements.txt
│
├── bot/                        # Telegram бот (aiogram 3)
│   ├── main.py                 # Запуск бота, polling
│   ├── config.py               # Токен, URL API
│   └── handlers/               # Хендлеры команд
│
└── frontend/                   # Веб-интерфейс
```

## Технологии

- **Backend**: FastAPI, SQLAlchemy 2.x, Alembic
- **Bot**: aiogram 3, httpx
- **Database**: SQLite (разработка), PostgreSQL (прод)
- **Frontend**: HTML/JS (в планах)

## Быстрый старт

1. Склонировать репозиторий и создать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Установить зависимости:
```bash
pip install -r taskbot/backend/requirements.txt
```

3. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактировать .env, указав BOT_TOKEN
```

4. Создать и применить миграции БД:
```bash
cd taskbot/backend
alembic upgrade head
cd ../..
```

5. Запустить FastAPI сервер:
```bash
cd taskbot/backend
uvicorn app.main:app --reload
```

6. Запустить Telegram бота (в отдельном терминале):
```bash
cd taskbot
python bot/main.py
```

## API Эндпоинты

### Задачи
- `GET /api/tasks?user_id={id}` — список задач пользователя
- `POST /api/tasks` — создать задачу
- `PUT /api/tasks/{id}` — обновить задачу
- `DELETE /api/tasks/{id}` — удалить задачу
- `PATCH /api/tasks/{id}/complete` — отметить задачу выполненной

### Пользователи
- `POST /api/users/register` — зарегистрировать пользователя

## Команды бота

- `/add` — добавить новую задачу
- `/list` — список задач (в разработке)
- `/done` — отметить задачу выполненной (в разработке)
- `/delete` — удалить задачу (в разработке)
- `/stats` — статистика за неделю (в разработке)

## Разработка

См. файл `COMMANDS.md` для всех команд разработки и тестирования.

## Лицензия

MIT
