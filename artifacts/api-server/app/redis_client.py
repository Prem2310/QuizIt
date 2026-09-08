import json
from collections.abc import AsyncIterator

from redis.asyncio import Redis

from app.core.config import get_settings


class RoomBroker:
    def __init__(self) -> None:
        self.client: Redis | None = None

    async def connect(self) -> None:
        url = get_settings().redis_url
        if not url:
            return
        self.client = Redis.from_url(url, decode_responses=True)
        await self.client.ping()

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None

    async def publish(self, room_id: str, payload: dict) -> None:
        if self.client:
            await self.client.publish(f"quizit:room:{room_id}", json.dumps(payload))

    async def subscribe(self, room_id: str) -> AsyncIterator[dict]:
        if not self.client:
            return
        pubsub = self.client.pubsub()
        await pubsub.subscribe(f"quizit:room:{room_id}")
        try:
            async for message in pubsub.listen():
                if message.get("type") == "message":
                    yield json.loads(message["data"])
        finally:
            await pubsub.unsubscribe(f"quizit:room:{room_id}")
            await pubsub.aclose()


room_broker = RoomBroker()