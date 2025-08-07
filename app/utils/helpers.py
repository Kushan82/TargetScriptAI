"""Helper utility functions."""

import uuid
import secrets
from datetime import datetime, timezone
from typing import Optional, Any, Dict
import hashlib


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique identifier."""
    if prefix:
        return f"{prefix}_{secrets.token_urlsafe(length)}"
    return secrets.token_urlsafe(length)


def generate_uuid() -> str:
    """Generate a standard UUID."""
    return str(uuid.uuid4())


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime as ISO string."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()


def get_current_timestamp() -> str:
    """Get current timestamp as formatted string."""
    return format_timestamp()


def hash_string(text: str) -> str:
    """Create SHA256 hash of string."""
    return hashlib.sha256(text.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    return " ".join(text.strip().split())


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary."""
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default


def convert_to_bool(value: Any) -> bool:
    """Convert various types to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
    
    return f"{size_bytes:.1f} {units[unit_index]}"
