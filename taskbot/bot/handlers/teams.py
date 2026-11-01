import httpx
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config


class CreateTeamStates(StatesGroup):
    waiting_team_name = State()


router = Router()


@router.message(F.text == "/create_team")
async def cmd_create_team(message: Message, state: FSMContext):
    await state.set_state(CreateTeamStates.waiting_team_name)
    await message.answer("Введите название команды:")


@router.message(CreateTeamStates.waiting_team_name)
async def process_team_name(message: Message, state: FSMContext):
    team_name = message.text
    await state.clear()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.API_URL}/api/teams",
                json={"name": team_name},
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            result = response.json()
            await message.answer(f"✅ Команда <b>{result['name']}</b> создана! ID команды: {result['id']}", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании команды: {str(e)}")


@router.message(F.text.startswith("/join_team "))
async def cmd_join_team(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Неверный формат команды. Используйте: /join_team [team_id]")
            return

        team_id = int(parts[1])
        user_id = message.from_user.id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.API_URL}/api/users/join-team/{user_id}/{team_id}",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            await message.answer(f"✅ Вы присоединились к команде с ID {team_id}!")
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат команды. Используйте: /join_team [team_id]")
    except Exception as e:
        await message.answer(f"❌ Ошибка при присоединении к команде: {str(e)}")


@router.message(F.text == "/team_list")
async def cmd_team_list(message: types.Message):
    try:
        user_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.API_URL}/api/tasks",
                params={"user_id": user_id},
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            tasks = response.json()

            if not tasks:
                await message.answer("📋 У вас нет задач.")
                return

            user = message.from_user
            text = f"👤 <b>{user.first_name or user.username}</b>\n\n"
            text += f"Ваши задачи:\n"
            for task in tasks:
                status = "✅" if task["is_done"] else "⏳"
                desc = f"\n📝 {task['description']}" if task["description"] else ""
                text += f"{status} <b>{task['id']}</b>. {task['title']}{desc}\n"

            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка задач: {str(e)}")


@router.message(F.text.startswith("/team_stats "))
async def cmd_team_stats(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Неверный формат команды. Используйте: /team_stats [team_id]")
            return

        team_id = int(parts[1])

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.API_URL}/api/teams/{team_id}/stats/weekly",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            stats = response.json()

            text = (
                f"📊 Статистика команды (ID: {team_id}):\n\n"
                f"Всего задач: {stats['total']}\n"
                f"✅ Выполнено: {stats['done']}\n"
                f"⏳ В работе: {stats['active']}\n"
                f"📈 Процент выполнения: {stats['percentage']}%"
            )
            await message.answer(text)
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат команды. Используйте: /team_stats [team_id]")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики команды: {str(e)}")
