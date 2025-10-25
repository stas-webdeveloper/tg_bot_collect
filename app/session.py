from db import save_lead
from enum import Enum

class SessionState(Enum):
    AWAITING_NAME = 1
    AWAITING_PHONE = 2
    AWAITING_COMMENT = 3
    COMPLETED = 4

class UserSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = SessionState.AWAITING_NAME
        self.name = None
        self.phone = None
        self.comment = "-"
        self.pending_reply = None

    async def handle_message(self, message: str):
        """Обрабатывает сообщение и возвращает ответ"""

        if self.state == SessionState.AWAITING_NAME:
            self.name = message.strip()
            self.state = SessionState.AWAITING_PHONE
            self.pending_reply = "📱 Отлично! Теперь введите ваш телефон:"

        elif self.state == SessionState.AWAITING_PHONE:
            self.phone = message.strip()
            self.state = SessionState.AWAITING_COMMENT
            self.pending_reply = "💬 Отлично! Теперь введите комментарий (или '-' если без комментария):"

        elif self.state == SessionState.AWAITING_COMMENT:
            self.comment = message.strip() if message.strip() != "-" else "-"

            # Сохраняем заявку
            save_lead(self.name, self.phone, self.comment)

            self.state = SessionState.COMPLETED
            self.pending_reply = f"""✅ Спасибо! Ваша заявка принята:

👤 Имя: {self.name}
📱 Телефон: {self.phone}
💬 Комментарий: {self.comment}

Скоро с вами свяжутся!"""

            # Сбрасываем сессию через 5 минут
            # await self.reset_after_delay()

        else:
            self.pending_reply = "Сессия завершена. Обновите страницу для новой заявки."

        return self.pending_reply

    def get_pending_reply(self):
        reply = self.pending_reply
        self.pending_reply = None  # Сбрасываем после отправки
        return reply

    def reset(self):
        """Сбрасывает сессию для новой заявки"""
        self.state = SessionState.AWAITING_NAME
        self.name = None
        self.phone = None
        self.comment = "-"
        self.pending_reply = "👋 Начнем новую заявку! Введите ваше имя:"
