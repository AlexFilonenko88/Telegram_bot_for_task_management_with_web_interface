import httpx
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config


class TagStates(StatesGroup):
    waiting_name = State()


router = Router()


@router.message(F.text == "/tag")
async def cmd_tag_help(message: Message):
    await message.answer(
        "🏷️ Управление тегами:\n\n"
        "/tag_add - Создать новый тег\n"
        "/tag_list - Показать список тегов\n"
        "/tag_delete <id> - Удалить тег"
    )


@router.message(F.text == "/tag_add")
async def cmd_add_tag(message: Message, state: FSMContext):
    await state.set_state(TagStates.waiting_name)
    await message.answer("Введите название тега:")


@router.message(TagStates.waiting_name)
async def process_tag_name(message: Message, state: FSMContext):
    tag_name = message.text
    await state.clear()

    try:
        user_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.API_URL}/api/tags",
                json={
                    "name": tag_name,
                    "user_id": user_id
                },
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            result = response.json()
            await message.answer(f"✅ Тег создан:\n\n🏷️ {result['name']} (ID: {result['id']})")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании тега: {str(e)}")


@router.message(F.text.startswith("/tag_list"))
async def cmd_list_tags(message: Message):
    try:
        user_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.API_URL}/api/tags",
                params={"user_id": user_id},
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            tags = response.json()

            if not tags:
                await message.answer("🏷️ У вас нет тегов")
            else:
                text = "🏷️ Ваши теги:\n\n"
                for tag in tags:
                    text += f"🏷️ {tag['name']} (ID: {tag['id']})\n"
                await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении тегов: {str(e)}")


@router.message(F.text.startswith("/tag_delete"))
async def cmd_delete_tag(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Укажите ID тега для удаления\nПример: /tag_delete 1")
            return

        tag_id = int(parts[1])
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{config.API_URL}/api/tags/{tag_id}",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            if response.status_code == 204:
                await message.answer(f"✅ Тег с ID {tag_id} удален")
            else:
                await message.answer(f"❌ Ошибка при удалении тега")
    except ValueError:
        await message.answer("❌ Неверный формат ID")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
