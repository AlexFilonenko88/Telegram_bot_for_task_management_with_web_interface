import httpx
from aiogram import Router, F, types
from aiogram.types import Message

import config


router = Router()


@router.message(F.text == "/list")
async def cmd_list(message: types.Message):
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
                await message.answer("📋 У вас нет активных задач.")
                return

            active_tasks = [t for t in tasks if not t["is_done"]]
            if not active_tasks:
                await message.answer("📋 У вас нет активных задач (все выполнены).")
                return

            text = "📋 Ваши активные задачи:\n\n"
            for task in active_tasks:
                status = "✅" if task["is_done"] else "⏳"
                desc = f"\n📝 {task['description']}" if task["description"] else ""
                text += f"{status} <b>{task['id']}</b>. {task['title']}{desc}\n"

            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка задач: {str(e)}")


@router.message(F.text == "/list all")
async def cmd_list_all(message: types.Message):
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

            text = "📋 Все ваши задачи:\n\n"
            for task in tasks:
                status = "✅" if task["is_done"] else "⏳"
                desc = f"\n📝 {task['description']}" if task["description"] else ""
                text += f"{status} <b>{task['id']}</b>. {task['title']}{desc}\n"

            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка задач: {str(e)}")


@router.message(F.text.startswith("/done "))
async def cmd_done(message: types.Message):
    try:
        task_id = int(message.text.split()[1])
        user_id = message.from_user.id

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{config.API_URL}/api/tasks/{task_id}/complete",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            result = response.json()
            await message.answer(f"✅ Задача <b>{result['title']}</b> отмечена как выполненная!", parse_mode="HTML")
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат команды. Используйте: /done <id>")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отметке задачи: {str(e)}")


@router.message(F.text.startswith("/delete "))
async def cmd_delete(message: types.Message):
    try:
        task_id = int(message.text.split()[1])

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{config.API_URL}/api/tasks/{task_id}",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            await message.answer(f"🗑 Задача с ID {task_id} удалена.")
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат команды. Используйте: /delete <id>")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении задачи: {str(e)}")


@router.message(F.text == "/stats")
async def cmd_stats(message: types.Message):
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

            total = len(tasks)
            done = len([t for t in tasks if t["is_done"]])
            active = total - done
            percentage = (done / total * 100) if total > 0 else 0

            text = (
                f"📊 Ваша статистика:\n\n"
                f"Всего задач: <b>{total}</b>\n"
                f"✅ Выполнено: <b>{done}</b>\n"
                f"⏳ В работе: <b>{active}</b>\n"
                f"📈 Процент выполнения: <b>{percentage:.1f}%</b>"
            )
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {str(e)}")
