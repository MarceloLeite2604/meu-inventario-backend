from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .logger import retrieve_logger

_LOGGER = retrieve_logger(__name__)

_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 10


async def check_rate_limit(
    request: Request,
    function_name: str,
    session: AsyncSession,
    max_requests: int = _RATE_LIMIT_MAX_REQUESTS,
    window_seconds: int = _RATE_LIMIT_WINDOW_SECONDS,
) -> None:
    from ..domains.questionnaires.models import RateLimit

    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"{client_ip}:{function_name}"
    window_start = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)

    await session.execute(
        delete(RateLimit).where(RateLimit.created_at < window_start)
    )

    result = await session.execute(
        select(func.count()).where(
            RateLimit.key == rate_limit_key,
            RateLimit.created_at >= window_start,
        )
    )
    request_count = result.scalar_one()

    if request_count >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    session.add(RateLimit(key=rate_limit_key))
    await session.flush()
