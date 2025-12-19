
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from threading import Lock
import hashlib


class CacheEntry:
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class InMemoryCache:
    
    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    return entry.value
                else:
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


cache = InMemoryCache()
