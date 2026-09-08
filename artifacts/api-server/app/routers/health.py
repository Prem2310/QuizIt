from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db import engine
from app.redis_client import room_broker
from app.schemas import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthStatus)
async def healthz() -> HealthStatus:
    database = "ok"
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        database = "unavailable"
    redis = "connected" if room_broker.client else ("configured" if get_settings().redis_url else "not_configured")
    return HealthStatus(status="ok", database=database, redis=redis)