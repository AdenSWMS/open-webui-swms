import os
import json
from typing import Optional, Dict, Any
import redis

# Werte dynamisch aus den Environment-Variablen laden
# Syntax: os.getenv("VARIABLEN_NAME", Fallback_Wert)
REDIS_HOST = os.getenv("SESSION_REDIS_HOST", "10.30.0.90")
REDIS_PORT = int(os.getenv("SESSION_REDIS_PORT", 6380))
REDIS_PASSWORD = os.getenv("SESSION_REDIS_PASSWORD", None) 


if REDIS_HOST.startswith("http://"):
    REDIS_HOST = REDIS_HOST.replace("http://", "")
if REDIS_HOST.startswith("https://"):
    REDIS_HOST = REDIS_HOST.replace("https://", "")
if ":" in REDIS_HOST:
    REDIS_HOST = REDIS_HOST.split(":")[0]

class UserSessionManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=0,
            decode_responses=True,
            socket_timeout=5.0
        )

    def create_or_update_session(self, user_email: str, max_budget: float, ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        key = f"session:user:{user_email}"
        session_data = {
            "user_email": user_email,
            "max_budget": float(max_budget),
            "spend": 0.0,
            "is_active": True
        }
        
        self.redis.set(key, json.dumps(session_data))
        
        if ttl_seconds:
            self.redis.expire(key, ttl_seconds)

        return session_data

    def get_session(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Liest den aktuellen Session-Status sowie die verbleibende TTL aus Redis."""
        key = f"session:user:{user_email}"
        raw_data = self.redis.get(key)
        if not raw_data:
            return None
        
        try:
            session_data = json.loads(raw_data)
            
            ttl = self.redis.ttl(key)
        
            session_data["ttl_seconds"] = ttl if ttl > 0 else None
            
            return session_data
        except Exception as e:
            print(f"Fehler beim Parsen der Redis-Session für {user_email}: {e}")
            return None

    def delete_session(self, user_email: str) -> bool:
        key = f"session:user:{user_email}"
        result = self.redis.delete(key)
        return result > 0

    def deactivate_session(self, user_email: str) -> bool:
        session = self.get_session(user_email)
        if not session:
            return False
        
        session["is_active"] = False
        self.redis.set(f"session:user:{user_email}", json.dumps(session))
        return True

# Einzige Singleton-Instanz
session_manager = UserSessionManager()