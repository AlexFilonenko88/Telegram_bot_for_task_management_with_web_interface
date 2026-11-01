import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.database import init_db
from app.routers import tasks, users, teams
from app import notifications


BOT_SECRET = os.getenv("BOT_SECRET", "secret-key")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


app = FastAPI(
    title="TaskBot API",
    description="API for task management with Telegram bot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(tasks.categories_router)
app.include_router(tasks.tags_router)
app.include_router(users.router)
app.include_router(teams.router)

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("../frontend/index.html")


@app.on_event("startup")
def on_startup():
    init_db()
    notifications.start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    notifications.stop_scheduler()


@app.middleware("http")
async def verify_bot_secret(request: Request, call_next):
    public_paths = ["/", "/docs", "/openapi.json", "/redoc", "/favicon.ico", "/dashboard", "/static"]

    if request.url.path in public_paths or request.url.path.startswith("/static"):
        return await call_next(request)

    # Allow API endpoints without bot secret for web interface
    if request.url.path.startswith("/api/tasks"):
        return await call_next(request)

    bot_secret = request.headers.get("X-Bot-Secret")
    if bot_secret != BOT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bot secret"
        )
    return await call_next(request)


@app.get("/")
def root():
    return {"message": "TaskBot API is running"}
