from typing import Dict
from session import UserSession

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}

    def get_session(self, session_id: str) -> UserSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = UserSession(session_id)
        return self.sessions[session_id]

    def cleanup_old_sessions(self):
        """Очистка старых сессий (можно запускать периодически)"""
        pass
