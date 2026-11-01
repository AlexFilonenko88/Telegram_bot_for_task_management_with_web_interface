import httpx
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config


class CategoryStates(StatesGroup):
    waiting_name = State()


router = Router()


@router.message(F.text == "/category")
async def cmd_category_help(message: Message):
    await message.answer(
        "📁 Управление категориями:\n\n"
        "/category_add - Создать новую категорию\n"
        "/category_list - Показать список категорий\n"
        "/category_delete <id> - Удалить категорию"
    )


@router.message(F.text == "/category_add")
async def cmd_add_category(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.waiting_name)
    await message.answer("Введите название категории:")


@router.message(CategoryStates.waiting_name)
async def process_category_name(message: Message, state: FSMContext):
    category_name = message.text
    await state.clear()

    try:
        user_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.API_URL}/api/categories",
                json={
                    "name": category_name,
                    "user_id": user_id
                },
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            result = response.json()
            await message.answer(f"✅ Категория создана:\n\n📁 {result['name']} (ID: {result['id']})")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании категории: {str(e)}")


@router.message(F.text.startswith("/category_list"))
async def cmd_list_categories(message: Message):
    try:
        user_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.API_URL}/api/categories",
                params={"user_id": user_id},
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            categories = response.json()

            if not categories:
                await message.answer("📁 У вас нет категорий")
            else:
                text = "📁 Ваши категории:\n\n"
                for cat in categories:
                    text += f"📁 {cat['name']} (ID: {cat['id']})\n"
                await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении категорий: {str(e)}")


@router.message(F.text.startswith("/category_delete"))
async def cmd_delete_category(message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Укажите ID категории для удаления\nПример: /category_delete 1")
            return

        category_id = int(parts[1])
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{config.API_URL}/api/categories/{category_id}",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            if response.status_code == 204:
                await message.answer(f"✅ Категория с ID {category_id} удалена")
            else:
                await message.answer(f"❌ Ошибка при удалении категории")
    except ValueError:
        await message.answer("❌ Неверный формат ID")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
