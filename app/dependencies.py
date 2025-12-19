
from fastapi import Depends
from app.middleware.auth import verify_api_key
from app.middleware.rate_limiter import rate_limiter


async def check_rate_limit(api_key: str = Depends(verify_api_key)) -> str:
    rate_limiter.check_rate_limit(api_key)
    return api_key
