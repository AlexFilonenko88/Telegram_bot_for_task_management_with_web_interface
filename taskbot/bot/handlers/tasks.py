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
                params={"user_id": user_id, "limit": 100},
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            # Ответ пагинированный: {"items": [...], "total": N, ...}
            tasks = response.json()["items"]

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
                params={"user_id": user_id, "limit": 100},
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            tasks = response.json()["items"]

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


@router.message(F.text.startswith("/done"))
async def cmd_done(message: types.Message):
    try:
        # Extract task ID from message (handles /done 1, /done[1], /done1)
        text = message.text
        # Remove /done prefix
        task_part = text[5:].strip()
        # Remove brackets if present
        task_part = task_part.replace("[", "").replace("]", "")
        
        if not task_part:
            await message.answer("❌ Укажите ID задачи. Используйте: /done [id]")
            return
            
        task_id = int(task_part)
        user_id = message.from_user.id

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{config.API_URL}/api/tasks/{task_id}/complete",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            result = response.json()
            await message.answer(f"✅ Задача отмечена как выполненная!")
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат команды. Используйте: /done [id]")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отметке задачи: {str(e)}")


@router.message(F.text.startswith("/delete"))
async def cmd_delete(message: types.Message):
    try:
        # Extract task ID from message (handles /delete 1, /delete[1], /delete1)
        text = message.text
        # Remove /delete prefix
        task_part = text[7:].strip()
        # Remove brackets if present
        task_part = task_part.replace("[", "").replace("]", "")
        
        if not task_part:
            await message.answer("❌ Укажите ID задачи. Используйте: /delete [id]")
            return
            
        task_id = int(task_part)

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{config.API_URL}/api/tasks/{task_id}",
                headers={"X-Bot-Secret": config.BOT_SECRET}
            )
            response.raise_for_status()
            await message.answer(f"🗑 Задача с ID {task_id} удалена.")
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат команды. Используйте: /delete [id]")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении задачи: {str(e)}")


@router.message(F.text == "/stats")
async def cmd_stats(message: types.Message):
    try:
        user_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            headers = {"X-Bot-Secret": config.BOT_SECRET}
            base_url = f"{config.API_URL}/api/tasks"

            # Счётчики берём из поля total пагинированного ответа:
            # limit=1 => сервер делает только COUNT, список не передаётся.
            response = await client.get(
                base_url,
                params={"user_id": user_id, "limit": 1},
                headers=headers
            )
            response.raise_for_status()
            total = response.json()["total"]

            response = await client.get(
                base_url,
                params={"user_id": user_id, "limit": 1, "is_done": "true"},
                headers=headers
            )
            response.raise_for_status()
            done = response.json()["total"]

            active = total - done
            percentage = (done / total * 100) if total > 0 else 0

            text = (
                f"📊 Ваша статистика:\n\n"
                f"Всего задач: {total}\n"
                f"✅ Выполнено: {done}\n"
                f"⏳ В работе: {active}\n"
                f"📈 Процент выполнения: {percentage:.1f}%"
            )
            await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {str(e)}")
