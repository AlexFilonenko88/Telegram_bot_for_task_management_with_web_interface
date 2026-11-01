import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import tasks, users


BOT_SECRET = os.getenv("BOT_SECRET", "secret-key")


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
app.include_router(users.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.middleware("http")
async def verify_bot_secret(request: Request, call_next):
    if request.url.path in ["/", "/docs", "/openapi.json"]:
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
