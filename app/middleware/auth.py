
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import logging

from app.config import settings


logger = logging.getLogger(__name__)


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key:
        logger.warning("Request made without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Include X-API-Key header in your request.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not settings.is_valid_api_key(api_key):
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key. Please check your credentials.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.info(f"Request authenticated with API key: {api_key[:8]}...")
    return api_key
