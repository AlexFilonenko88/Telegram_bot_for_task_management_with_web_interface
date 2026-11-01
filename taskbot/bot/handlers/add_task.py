import httpx
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from datetime import datetime

import config


class AddTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_priority = State()
    waiting_deadline = State()
    waiting_category = State()
    waiting_tags = State()


router = Router()


@router.message(F.text == "/add")
async def cmd_add_task(message: Message, state: FSMContext):
    await state.set_state(AddTaskStates.waiting_title)
    await message.answer("Введите название задачи:")


@router.message(AddTaskStates.waiting_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddTaskStates.waiting_description)
    await message.answer("Введите описание задачи (или отправьте /skip для пропуска):")


@router.message(AddTaskStates.waiting_description)
async def process_description(message: Message, state: FSMContext):
    if message.text == "/skip":
        description = None
    else:
        description = message.text

    await state.update_data(description=description)
    await state.set_state(AddTaskStates.waiting_priority)
    await message.answer(
        "Выберите приоритет (или отправьте /skip для пропуска):\n"
        "1. high (высокий)\n"
        "2. medium (средний)\n"
        "3. low (низкий)"
    )


@router.message(AddTaskStates.waiting_priority)
async def process_priority(message: Message, state: FSMContext):
    text = message.text.lower()
    if text == "/skip":
        priority = None
    elif text in ["high", "medium", "low"]:
        priority = text
    else:
        await message.answer("❌ Неверный приоритет. Используйте: high, medium, low или /skip")
        return

    await state.update_data(priority=priority)
    await state.set_state(AddTaskStates.waiting_deadline)
    await message.answer(
        "Введите дедлайн в формате YYYY-MM-DD HH:MM (или отправьте /skip для пропуска):\n"
        "Пример: 2026-11-05 18:00"
    )


@router.message(AddTaskStates.waiting_deadline)
async def process_deadline(message: Message, state: FSMContext):
    if message.text == "/skip":
        deadline = None
    else:
        try:
            deadline = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer("❌ Неверный формат даты. Используйте YYYY-MM-DD HH:MM или /skip")
            return

    await state.update_data(deadline=deadline.isoformat() if deadline else None)
    await state.set_state(AddTaskStates.waiting_category)
    await message.answer("Введите ID категории (или отправьте /skip для пропуска):")


@router.message(AddTaskStates.waiting_category)
async def process_category(message: Message, state: FSMContext):
    if message.text == "/skip":
        category_id = None
    else:
        try:
            category_id = int(message.text)
        except ValueError:
            await message.answer("❌ Неверный ID категории. Введите число или /skip")
            return

    await state.update_data(category_id=category_id)
    await state.set_state(AddTaskStates.waiting_tags)
    await message.answer("Введите ID тегов через запятую (или отправьте /skip для пропуска):\nПример: 1,2,3")


@router.message(AddTaskStates.waiting_tags)
async def process_tags(message: Message, state: FSMContext):
    if message.text == "/skip":
        tag_ids = None
    else:
        try:
            tag_ids = [int(tag.strip()) for tag in message.text.split(",")]
        except ValueError:
            await message.answer("❌ Неверный формат тегов. Введите ID через запятую или /skip")
            return

    data = await state.get_data()
    title = data["title"]
    description = data.get("description")
    priority = data.get("priority")
    deadline = data.get("deadline")
    category_id = data.get("category_id")

    await state.clear()

    try:
        user_id = message.from_user.id
        task_data = {
            "title": title,
            "description": description,
            "user_id": user_id
        }

        if priority:
            task_data["priority"] = priority
        if deadline:
            task_data["deadline"] = deadline
        if category_id:
            task_data["category_id"] = category_id
        if tag_ids:
            task_data["tag_ids"] = tag_ids

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.API_URL}/api/tasks",
                json=task_data,
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            result = response.json()

            response_text = f"✅ Задача создана:\n\n📌 {result['title']}"
            if result.get('priority'):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(result['priority'], "")
                response_text += f"\n{priority_emoji} Приоритет: {result['priority']}"
            if result.get('deadline'):
                response_text += f"\n📅 Дедлайн: {result['deadline']}"
            if result.get('category_id'):
                response_text += f"\n📁 Категория ID: {result['category_id']}"
            if result.get('tags'):
                tag_names = [tag['name'] for tag in result['tags']]
                response_text += f"\n🏷️ Теги: {', '.join(tag_names)}"

            await message.answer(response_text)
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании задачи: {str(e)}")
