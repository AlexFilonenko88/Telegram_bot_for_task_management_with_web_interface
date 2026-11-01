# TaskBot - Telegram бот для управления задачами с веб-интерфейсом

Простой и эффективный инструмент для управления задачами через Telegram с возможностью просмотра статистики через веб-интерфейс. Система ориентирована на одного пользователя или небольшую команду до 5 человек.

## Особенности

- 🤖 **Telegram бот** для быстрого управления задачами без переключения между приложениями
- 📊 **Веб-дашборд** с визуализацией прогресса и графиками
- 📈 **Статистика** выполнения задач за неделю
- 👥 **Командный режим** для совместной работы команд до 5 человек
- 🔒 **Простая авторизация** через Telegram user_id (без паролей)
- 🚀 **REST API** для интеграций с другими сервисами
- 💾 **SQLite** в разработке (поддержка PostgreSQL в продакшн)

## Стек технологий

- **Backend**: FastAPI
- **ORM**: SQLAlchemy 2.x
- **База данных**: SQLite (разработка) / PostgreSQL (продакшн)
- **Telegram Bot**: aiogram 3.x
- **Frontend**: HTML + CSS + JavaScript (без фреймворков)
- **Python версия**: 3.10+

## Архитектура

### Ключевые принципы

- **Единственный источник правды — база данных.** Бот и веб читают данные через один и тот же API, а не напрямую из БД.
- **Бот — клиент API, не самостоятельный сервис.** Это позволяет переиспользовать логику и тестировать её через Swagger.
- **FastAPI — единственная точка входа в данные.** Вся бизнес-логика живёт здесь, не размазана по боту и веб-клиенту.

### Структура проекта

```
taskbot/
├── backend/                    # FastAPI приложение
│   ├── app/
│   │   ├── main.py             # Точка входа FastAPI
│   │   ├── database.py         # Подключение к БД, сессия
│   │   ├── models.py           # SQLAlchemy модели
│   │   ├── schemas.py          # Pydantic схемы (валидация)
│   │   ├── crud.py             # CRUD операции с БД
│   │   └── routers/
│   │       ├── tasks.py        # Роутер /api/tasks
│   │       ├── users.py        # Роутер /api/users
│   │       └── teams.py        # Роутер /api/teams
│   ├── alembic/                # Миграции базы данных
│   └── requirements.txt
│
├── bot/                        # Telegram бот (aiogram 3)
│   ├── main.py                 # Запуск бота, polling
│   ├── config.py               # Токен, URL API
│   ├── api_client.py           # HTTP-клиент к FastAPI
│   └── handlers/
│       ├── common.py           # /start, /help
│       ├── add_task.py         # /add (FSM)
│       ├── tasks.py            # /list, /done, /delete, /stats
│       └── teams.py            # /create_team, /join_team, /team_stats
│
└── frontend/                   # Веб-интерфейс
    ├── index.html              # Дашборд
    └── static/
        ├── style.css
        └── app.js
```

## Быстрый старт

### 1. Клонирование и установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd Telegram_bot_for_task_management_with_web_interface

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r taskbot/backend/requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
BOT_TOKEN=your_telegram_bot_token
API_URL=http://localhost:8000
BOT_SECRET=your_secret_key
```

### 3. Инициализация базы данных

```bash
cd taskbot/backend
alembic upgrade head
```

### 4. Запуск сервера

```bash
cd taskbot/backend
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`
- Web Dashboard: `http://localhost:8000/dashboard`

### 5. Запуск Telegram бота

В новом терминале:

```bash
cd taskbot
python bot/main.py
```

## Команды бота

### Основные команды

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и краткая справка |
| `/help` | Список доступных команд |
| `/add` | Добавить новую задачу через диалог |
| `/list` | Показать список активных задач |
| `/list all` | Показать список всех задач |
| `/done [id]` | Отметить задачу как выполненную |
| `/delete [id]` | Удалить задачу |
| `/stats` | Показать краткую статистику |

### Командный режим

| Команда | Описание |
|---------|----------|
| `/create_team` | Создать команду через диалог |
| `/join_team [id]` | Присоединиться к команде по ID |
| `/team_stats [id]` | Показать статистику команды |

## Веб-интерфейс

### Доступ к дашборду

1. Запустите FastAPI сервер
2. Откройте в браузере: `http://localhost:8000/dashboard`
3. Введите ваш Telegram ID
4. Нажмите "Загрузить данные"

### Функции дашборда

- 📊 Карточки с основными метриками (всего/выполнено/в работе/процент)
- 📈 График выполнения задач за неделю
- 📋 Список задач с фильтрацией (все/активные/выполненные)
- 🔄 Автоматическое обновление данных

## API

### Основные эндпоинты

#### Пользователи

- `POST /api/users/register` - Регистрация пользователя
- `POST /api/users/join-team/{user_id}/{team_id}` - Присоединение к команде

#### Задачи

- `GET /api/tasks?user_id={id}` - Получить задачи пользователя
- `GET /api/tasks/stats/weekly?user_id={id}` - Статистика за неделю
- `POST /api/tasks` - Создать задачу
- `PUT /api/tasks/{id}` - Обновить задачу
- `DELETE /api/tasks/{id}` - Удалить задачу
- `PATCH /api/tasks/{id}/complete` - Отметить выполненной

#### Команды

- `POST /api/teams` - Создать команду
- `GET /api/teams/{id}/tasks` - Получить задачи команды
- `GET /api/teams/{id}/stats/weekly` - Статистика команды за неделю

### Авторизация

API защищён заголовком `X-Bot-Secret`. Укажите его значение в `.env` файле.

```bash
curl -X GET "http://localhost:8000/api/tasks?user_id=1" \
  -H "X-Bot-Secret: your-secret-key"
```

## Командный режим

Командный режим позволяет нескольким пользователям работать над общим списком задач.

### Как создать команду

1. Используйте команду `/create_team` в Telegram боте
2. Введите название команды
3. Бот вернёт ID команды

### Как присоединиться к команде

1. Используйте команду `/join_team <team_id>` в Telegram боте
2. После присоединения ваши задачи будут видны другим участникам команды

### Статистика команды

- Команда `/team_stats <team_id>` показывает статистику выполнения задач всей команды
- Веб-интерфейс также поддерживает просмотр задач команды (в разработке)

## Миграции базы данных

### Создание новой миграции

```bash
cd taskbot/backend
alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
cd taskbot/backend
alembic upgrade head
```

### Откат миграции

```bash
cd taskbot/backend
alembic downgrade -1
```

## Разработка

### Запуск в режиме разработки

```bash
# Backend
cd taskbot/backend
uvicorn app.main:app --reload

# Bot (в другом терминале)
cd taskbot
python bot/main.py
```

### Тестирование API

Используйте Swagger UI: `http://localhost:8000/docs`

## Полезные ссылки

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [aiogram 3 документация](https://docs.aiogram.dev/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)

## Лицензия

MIT License

## Поддержка

Если у вас есть вопросы или проблемы, создайте issue в репозитории.
