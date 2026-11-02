"""Точка входа FastAPI-приложения TaskBot API.

Безопасность:
- BOT_SECRET читается только из окружения; запуск без него запрещён
  (fail-fast вместо небезопасного дефолта "secret-key").
- Сравнение секрета — hmac.compare_digest (защита от timing-атак).
- Анонимно разрешено только ЧТЕНИЕ задач (GET /api/tasks*); все мутации
  (POST/PUT/PATCH/DELETE) требуют заголовок X-Bot-Secret.
- CORS-источники задаются переменной CORS_ALLOW_ORIGINS, а не "*".
"""

import hmac
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import notifications
from app.database import init_db
from app.routers import categories, tags, tasks, teams, users


# --- Конфигурация из окружения (никаких секретов в коде) ----------------------

BOT_SECRET = os.getenv("BOT_SECRET")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

if not BOT_SECRET:
    # Секрет обязателен: без него мутации нечем аутентифицировать.
    # Падаем на старте с понятной ошибкой, а не работаем с дефолтом.
    raise RuntimeError(
        "Переменная окружения BOT_SECRET не задана. "
        "Укажите её в .env / окружении (см. .env.example)."
    )

# Источники CORS через запятую: CORS_ALLOW_ORIGINS=http://localhost:8000,https://myapp.com
CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:8000").split(",")
    if origin.strip()
]

# Пути, доступные без аутентификации (статика, дашборд, документация).
PUBLIC_PATHS = {
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
    "/dashboard",
    "/static",
}


app = FastAPI(
    title="TaskBot API",
    description="API for task management with Telegram bot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(categories.router)
app.include_router(tags.router)

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


@app.middleware("http")
async def verify_bot_secret(request: Request, call_next):
    """Аутентификация запросов к API по заголовку X-Bot-Secret.

    Анонимно разрешены публичные пути и только ЧТЕНИЕ задач
    (GET /api/tasks*) — веб-дашборду этого достаточно. Любые мутации
    требуют секрет. Сравнение константное по времени (hmac.compare_digest).
    """
    path = request.url.path

    if path in PUBLIC_PATHS or path.startswith("/static"):
        return await call_next(request)

    # CORS preflight: OPTIONS не несёт ни данных, ни кастомных заголовков
    # (браузер их не отправляет), сайд-эффектов нет. Пропускаем — ответ
    # сформирует CORSMiddleware (для чужих Origin он вернёт 400).
    if request.method == "OPTIONS":
        return await call_next(request)

    # Анонимное чтение задач для веб-интерфейса (без мутаций).
    if request.method == "GET" and path.startswith("/api/tasks"):
        return await call_next(request)

    provided_secret = request.headers.get("X-Bot-Secret", "")
    if not hmac.compare_digest(provided_secret, BOT_SECRET):
        # В middleware HTTPException не превращается в 401 корректно
        # (уходит как 500), поэтому возвращаем JSON-ответ напрямую.
        return JSONResponse(
            status_code=401, content={"detail": "Invalid bot secret"}
        )
    return await call_next(request)


@app.get("/dashboard")
async def serve_dashboard() -> FileResponse:
    """Отдать страницу веб-дашборда."""
    return FileResponse("../frontend/index.html")


@app.get("/")
def root() -> dict:
    """Health-check корень API."""
    return {"message": "TaskBot API is running"}


@app.on_event("startup")
def on_startup() -> None:
    """При старте: создать таблицы (если нет) и запустить планировщик напоминаний."""
    init_db()
    notifications.start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    """При остановке: остановить планировщик напоминаний."""
    notifications.stop_scheduler()
