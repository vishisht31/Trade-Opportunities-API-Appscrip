
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, List
from threading import Lock
import logging

from app.config import settings


logger = logging.getLogger(__name__)


class RateLimitEntry:
    
    def __init__(self, limit_per_hour: int):
        self.limit = limit_per_hour
        self.requests: List[datetime] = []
        self.lock = Lock()
    
    def can_make_request(self) -> bool:
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(hours=1)
            

            self.requests = [req_time for req_time in self.requests if req_time > cutoff]
            
            return len(self.requests) < self.limit
    
    def record_request(self) -> None:
        with self.lock:
            self.requests.append(datetime.utcnow())
    
    def get_remaining(self) -> int:
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(hours=1)
            self.requests = [req_time for req_time in self.requests if req_time > cutoff]
            return max(0, self.limit - len(self.requests))
    
    def get_reset_time(self) -> datetime:
        with self.lock:
            if self.requests:
                oldest = min(self.requests)
                return oldest + timedelta(hours=1)
            return datetime.utcnow() + timedelta(hours=1)


class RateLimiter:
    
    def __init__(self):
        self._limits: Dict[str, RateLimitEntry] = {}
        self._lock = Lock()
    
    def check_rate_limit(self, identifier: str) -> None:
        """
        Check rate limit for a given identifier (IP address or other identifier)
        """
        if identifier not in self._limits:
            with self._lock:
                if identifier not in self._limits:
                    self._limits[identifier] = RateLimitEntry(settings.rate_limit_per_hour)
        
        entry = self._limits[identifier]
        
        if not entry.can_make_request():
            reset_time = entry.get_reset_time()
            logger.warning(f"Rate limit exceeded for IP: {identifier}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Limit: {settings.rate_limit_per_hour} requests per hour. Try again after {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                headers={
                    "X-RateLimit-Limit": str(settings.rate_limit_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": reset_time.isoformat(),
                }
            )
        
        entry.record_request()
        logger.info(f"Request recorded for IP {identifier}. Remaining: {entry.get_remaining()}")
    
    def get_rate_limit_headers(self, identifier: str) -> Dict[str, str]:
        if identifier not in self._limits:
            return {
                "X-RateLimit-Limit": str(settings.rate_limit_per_hour),
                "X-RateLimit-Remaining": str(settings.rate_limit_per_hour),
            }
        
        entry = self._limits[identifier]
        return {
            "X-RateLimit-Limit": str(settings.rate_limit_per_hour),
            "X-RateLimit-Remaining": str(entry.get_remaining()),
            "X-RateLimit-Reset": entry.get_reset_time().isoformat(),
        }


rate_limiter = RateLimiter()
