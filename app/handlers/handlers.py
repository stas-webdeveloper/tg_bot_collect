from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from db import save_lead, get_all_leads, clear_old_data
from config import ADMIN_ID

router = Router()
# ID администратора (твой Telegram ID можно узнать через @userinfobot)

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для приёма заявок.\n"
        "Отправь мне сообщение в формате:\n\n"
        "Имя\nТелефон\nКомментарий (необязательно)"
    )


@router.message(Command("showdb"))
async def show_db(message: Message):
    """Команда для проверки содержимого базы (только админ)."""
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

    from db import clear_old_data
    count = clear_old_data(days=30)
    await message.answer(f"🧹 Удалено {count} заявок старше 30 дней.")



@router.message(F.text)
async def handle_message(message: Message):
    text = message.text.strip()
    parts = text.split("\n")

    if len(parts) < 2:
        await message.answer("⚠️ Нужно минимум имя и телефон.\nПример:\n\nИван\n+49123456789\nХочу консультацию")
        return

    name = parts[0]
    phone = parts[1]
    msg = "\n".join(parts[2:]) if len(parts) > 2 else "-"

    save_lead(name, phone, msg)
    await message.answer("✅ Заявка записана! Менеджер свяжется с тобой.")
