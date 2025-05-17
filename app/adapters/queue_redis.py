from uuid import UUID
import redis
from app.infra.config import settings

class RedisEventQueue:
    def __init__(self, key: str = "lane_events"):
        self.key = key
        self.client = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

    def enqueue(self, lane_id: UUID) -> None:
        self.client.lpush(self.key, str(lane_id))

    def dequeue_blocking(self, timeout: int = 5) -> UUID:
        _, val = self.client.brpop(self.key, timeout=timeout)
        if val is None:
            raise TimeoutError("No events")
        from uuid import UUID as _UUID
        return _UUID(val.decode())
