# Команды проекта TaskBot

## Настройка окружения

### Создание виртуального окружения
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

### Установка зависимостей
```bash
pip install -r taskbot/backend/requirements.txt
```

### Настройка переменных окружения
```bash
cp .env.example .env
# Отредактировать .env:
# BOT_TOKEN=your_telegram_bot_token
# API_URL=http://localhost:8000
# BOT_SECRET=your_secret_key
```

## Работа с базой данных

### Создание миграции
```bash
cd taskbot/backend
alembic revision --autogenerate -m "описание миграции"
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

### Просмотр текущей версии миграции
```bash
cd taskbot/backend
alembic current
```

### Просмотр истории миграций
```bash
cd taskbot/backend
alembic history
```

### Миграции
Проект содержит следующие миграции:
- `8e3a28c04bca_initial_migration.py` - Начальная миграция (User, Task)
- `20261101_add_team_model.py` - Добавление модели Team и поля team_id в User

## Запуск сервера

### Запуск FastAPI в режиме разработки
```bash
cd taskbot/backend
uvicorn app.main:app --reload
```

### Запуск FastAPI в production
```bash
cd taskbot/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Запуск Telegram бота
```bash
cd taskbot
source ../.venv/bin/activate  # Linux/Mac
# или
..\\.venv\\Scripts\\activate  # Windows
python bot/main.py
```

### Доступ к веб-интерфейсу
После запуска FastAPI сервера:
- Web Dashboard: `http://localhost:8000/dashboard`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Команды Telegram бота

### Основные команды

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и краткая справка |
| `/help` | Список доступных команд |
| `/add` | Добавить новую задачу через диалог (FSM) |
| `/list` | Показать список активных задач |
| `/list all` | Показать список всех задач (включая выполненные) |
| `/done [id]` | Отметить задачу как выполненную |
| `/delete [id]` | Удалить задачу |
| `/stats` | Показать краткую статистику выполнения |

### Команды для работы с командами

| Команда | Описание |
|---------|----------|
| `/create_team` | Создать новую команду через диалог (FSM) |
| `/join_team [id]` | Присоединиться к существующей команде по ID |
| `/team_stats [id]` | Показать статистику выполнения задач команды |

### Примеры использования команд бота

#### Добавление задачи через диалог
```
/add
→ Введите название задачи: "Сделать домашнее задание"
→ Введите описание задачи (или /skip): "Математика, глава 5"
✅ Задача создана: Сделать домашнее задание
```

#### Просмотр списка задач
```
/list
📋 Ваши активные задачи:

⏳ 1. Сделать домашнее задание
📝 Математика, глава 5

⏳ 2. Подготовить презентацию
```

#### Отметка задачи выполненной
```
/done 1
✅ Задача отмечена как выполненная!
```

#### Создание команды
```
/create_team
→ Введите название команды: "Команда разработчиков"
✅ Команда Команда разработчиков создана! ID команды: 1
```

#### Присоединение к команде
```
/join_team 1
✅ Вы присоединились к команде с ID 1!
```

#### Статистика команды
```
/team_stats 1
📊 Статистика команды (ID: 1):

Всего задач: 15
✅ Выполнено: 10
⏳ В работе: 5
📈 Процент выполнения: 66.7%
```

## Тестирование API

### Запуск сервера для тестов
```bash
cd taskbot/backend
uvicorn app.main:app --reload
```

### Тестирование через curl

#### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -H "X-Bot-Secret: secret-key" \
  -d '{
    "telegram_id": 123456789,
    "username": "testuser",
    "first_name": "Test"
  }'
```

#### Получение списка задач
```bash
curl -X GET "http://localhost:8000/api/tasks?user_id=1" \
  -H "X-Bot-Secret: secret-key"
```

#### Создание задачи
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-Bot-Secret: secret-key" \
  -d '{
    "title": "Новая задача",
    "description": "Описание задачи",
    "user_id": 1
  }'
```

#### Обновление задачи
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -H "X-Bot-Secret: secret-key" \
  -d '{
    "title": "Обновлённая задача",
    "is_done": true
  }'
```

#### Удаление задачи
```bash
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -H "X-Bot-Secret: secret-key"
```

#### Отметить задачу выполненной
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "X-Bot-Secret: secret-key"
```

#### Получить статистику за неделю
```bash
curl -X GET "http://localhost:8000/api/tasks/stats/weekly?user_id=1" \
  -H "X-Bot-Secret: secret-key"
```

#### Создать команду
```bash
curl -X POST http://localhost:8000/api/teams \
  -H "Content-Type: application/json" \
  -H "X-Bot-Secret: secret-key" \
  -d '{
    "name": "My Team"
  }'
```

#### Получить задачи команды
```bash
curl -X GET http://localhost:8000/api/teams/1/tasks \
  -H "X-Bot-Secret: secret-key"
```

#### Получить статистику команды
```bash
curl -X GET http://localhost:8000/api/teams/1/stats/weekly \
  -H "X-Bot-Secret: secret-key"
```

#### Присоединить пользователя к команде
```bash
curl -X POST http://localhost:8000/api/users/join-team/1/1 \
  -H "X-Bot-Secret: secret-key"
```

## Работа с Git

### Добавление всех изменений
```bash
git add -A
```

### Создание коммита
```bash
git commit -m "описание изменений"
```

### Отправка изменений в удалённый репозиторий
```bash
git push origin master
```

### Просмотр статуса
```bash
git status
```

### Просмотр изменений
```bash
git diff
```

## Полезные команды

### Просмотр установленных пакетов
```bash
pip list
```

### Обновление pip
```bash
pip install --upgrade pip
```

### Очистка кэша pip
```bash
pip cache purge
```

### Удаление виртуального окружения
```bash
deactivate
rm -rf .venv
```

### Сброс базы данных (внимание: удаляет все данные!)
```bash
rm taskbot/backend/tasks.db
cd taskbot/backend
alembic downgrade base
alembic upgrade head
```

## Документация API

### Запуск Swagger UI
После запуска сервера откройте в браузере:
```
http://localhost:8000/docs
```

### Запуск ReDoc
```
http://localhost:8000/redoc
```

## Логи и отладка

### Запуск с verbose логами
```bash
cd taskbot/backend
uvicorn app.main:app --reload --log-level debug
```

### Просмотр логов бота
```bash
cd taskbot
python bot/main.py
# Логи выводятся в stdout
```

## Docker (в планах)

### Сборка образа
```bash
docker build -t taskbot .
```

### Запуск контейнера
```bash
docker run -p 8000:8000 taskbot
```

### Запуск с docker-compose
```bash
docker-compose up
```
