
import re
from typing import Optional


def sanitize_sector_name(sector: str) -> str:
    if not sector:
        raise ValueError("Sector name cannot be empty")
    
    sanitized = sector.lower().strip()

    sanitized = re.sub(r'[^a-z0-9\s\-]', '', sanitized)
    
    sanitized = re.sub(r'\s+', ' ', sanitized)

    sanitized = sanitized.replace(' ', '-')
    
    if not sanitized:
        raise ValueError("Invalid sector name after sanitization")
    
    return sanitized


def validate_sector_length(sector: str, max_length: int = 50) -> Optional[str]:
    if len(sector) > max_length:
        return f"Sector name too long (max {max_length} characters)"
    return None


def is_safe_input(text: str) -> bool:
  
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  
        r'eval\(',
        r'exec\(',
        r'import\s+',
        r'__import__',
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    return True
