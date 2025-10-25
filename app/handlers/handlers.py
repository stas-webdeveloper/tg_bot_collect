from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import save_lead, get_all_leads, clear_old_data
from config import ADMIN_ID

router = Router()

class LeadStates(StatesGroup):
    AWAITING_NAME = State()
    AWAITING_PHONE = State()
    AWAITING_COMMENT = State()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(LeadStates.AWAITING_NAME)
    await message.answer(
        "👋 Привет! Я бот для приёма заявок.\n\n"
        "Введите ваше имя:"
    )

@router.message(LeadStates.AWAITING_NAME)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(LeadStates.AWAITING_PHONE)
    await message.answer("📱 Отлично! Теперь введите ваш телефон:")

@router.message(LeadStates.AWAITING_PHONE)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(LeadStates.AWAITING_COMMENT)
    await message.answer("💬 Теперь введите комментарий (или '-' если без комментария):")

@router.message(LeadStates.AWAITING_COMMENT)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text.strip() if message.text.strip() != "-" else "-"
    user_data = await state.get_data()

    # Сохраняем заявку
    save_lead(user_data['name'], user_data['phone'], comment)

    await message.answer(
        f"✅ Заявка принята!\n\n"
        f"👤 Имя: {user_data['name']}\n"
        f"📱 Телефон: {user_data['phone']}\n"
        f"💬 Комментарий: {comment}\n\n"
        f"Скоро с вами свяжутся!"
    )

    await state.clear()

# Админские команды остаются без изменений
@router.message(Command("showdb"))
async def show_db(message: Message):
    if int(message.from_user.id) != int(ADMIN_ID):
        await message.answer("⛔ У тебя нет доступа к этой команде.")
        return

    leads = get_all_leads()
    if not leads:
        await message.answer("📭 База пуста.")
        return

    text = "\n\n".join(
        [f"{i+1}. {l['name']} — {l['phone']}\n{l['message']}" for i, l in enumerate(leads[-10:])]
    )
    await message.answer(f"📋 Последние заявки:\n\n{text}")

@router.message(Command("cleardb"))
async def clear_db(message: Message):
    if int(message.from_user.id) != int(ADMIN_ID):
        await message.answer("⛔ Нет доступа.")
        return

    count = clear_old_data(days=30)
    await message.answer(f"🧹 Удалено {count} заявок старше 30 дней.")
