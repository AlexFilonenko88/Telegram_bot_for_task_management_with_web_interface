from aiogram import Router, F, types

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 Привет! Я TaskBot — бот для управления задачами.\n\n"
        "Доступные команды:\n"
        "/add — добавить новую задачу\n"
        "/help — справка по командам\n\n"
        "Другие команды в разработке..."
    )
    await message.answer(welcome_text)


@router.message(F.text == "/help")
async def cmd_help(message: types.Message):
    help_text = (
        "📋 Справка по командам:\n\n"
        "/start — приветствие\n"
        "/help — эта справка\n"
        "/add — добавить новую задачу через диалог\n"
        "/list — список активных задач\n"
        "/list all — все задачи\n"
        "/done <id> — отметить задачу выполненной\n"
        "/delete <id> — удалить задачу\n"
        "/stats — статистика выполнения"
    )
    await message.answer(help_text)
