from redis.asyncio import Redis
from fastapi import Request, Depends, HTTPException,status
from typing import Optional
from .auth import decode_jwt
from .config import settings


redis = Redis(
    host=settings.redis_settings.host,
    port=settings.redis_settings.port,
    decode_responses=settings.redis_settings.decode_responses
    )

async def rate_limit(request: Request):

        key = f"rate:{request.cookies.get('device_id')}:{request.client.host}:{request.url.path}"
        
        count = await redis.incr(key)
        
        if count ==1:
            await redis.expire(key,60)
        
        if count>3:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

async def invalidate_trainers_cache():
    await redis.delete("trainers:all")