import redis
from datetime import datetime, timedelta


class SessionManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def create_session(self, user_id: int, device_id: str):
        session_id = self._generate_session_id()
        self.redis.setex(
            f"session:{session_id}",
            {
                "user_id": user_id,
                "device_id": device_id,
                "last_active": datetime.utcnow().isoformat()
            },
            ex=60 * 60 * 24  # 24小时过期
        )
        return session_id

    def _generate_session_id(self) -> str:
        return secrets.token_urlsafe(32)