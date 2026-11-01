from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.api_client import APIClient


class AddTaskStates(StatesGroup):
    waiting_title = State()
    waiting_description = State()


router = Router()
api_client = APIClient()


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

    data = await state.get_data()
    title = data["title"]

    await state.clear()

    try:
        user_id = message.from_user.id
        result = await api_client.create_task(title, description, user_id)
        await message.answer(f"✅ Задача создана:\n\n{result['title']}")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании задачи: {str(e)}")
