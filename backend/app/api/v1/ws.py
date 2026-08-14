import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from redis.asyncio import Redis
from jose import jwt, JWTError

from ...core.config import settings

router = APIRouter()


async def get_user_id_from_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if not user_id:
            return None

        return int(user_id)

    except JWTError:
        return None


@router.websocket("/ws/jobs")
async def websocket_jobs(
    websocket: WebSocket,
    token: str = Query(...)
):
    user_id = await get_user_id_from_token(token)

    if not user_id:
        await websocket.close(code=4001)
        return

    await websocket.accept()

    redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )

    pubsub = redis.pubsub()
    channel = f"user:{user_id}:jobs"

    await pubsub.subscribe(channel)

    try:
        await websocket.send_text(
            json.dumps({
                "type": "connected",
                "channel": channel
            })
        )

        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0
            )

            if message and message["type"] == "message":
                await websocket.send_text(message["data"])

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        pass

    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis.close()