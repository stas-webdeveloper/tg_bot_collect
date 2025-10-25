import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db, export_to_excel_loop, save_lead
from handlers.handlers import router as bot_router
from session_manager import SessionManager
import os
import uvicorn

app = FastAPI(title="Lead Bot API")
session_manager = SessionManager()

# CORS для фронтенда на Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажи конкретный домен Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация бота
bot = None
dp = None

@app.on_event("startup")
async def startup():
    global bot, dp
    init_db()

    # Инициализация телеграм бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(bot_router)

    # Запускаем фоновые задачи
    asyncio.create_task(export_to_excel_loop())
    asyncio.create_task(dp.start_polling(bot))

    print("🚀 Сервис запущен: FastAPI + Telegram Bot")

# Эндпоинты для фронтенда
@app.post("/send_message")
async def send_message(data: dict):
    session_id = data.get("session_id")
    message = data.get("message", "").strip()

    if not session_id or not message:
        raise HTTPException(status_code=400, detail="Missing session_id or message")

    # Получаем или создаем сессию
    session = session_manager.get_session(session_id)

    # Обрабатываем сообщение
    response = await session.handle_message(message)

    return {"status": "ok", "session_id": session_id, "response": response}

@app.get("/get_reply/{session_id}")
async def get_reply(session_id: str):
    session = session_manager.get_session(session_id)
    reply = session.get_pending_reply()

    return {"session_id": session_id, "reply": reply}

@app.get("/api/excel")
async def get_excel():
    """Отдает Excel файл со всеми заявками"""
    excel_path = "data/clients.xlsx"
    if os.path.exists(excel_path):
        return FileResponse(
            excel_path,
            filename="leads.xlsx",
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    raise HTTPException(status_code=404, detail="Excel file not found")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Lead Bot API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
