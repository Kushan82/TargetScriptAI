"""Validation utility functions."""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url.strip())
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic validation)."""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_non_empty_string(value: Optional[str]) -> bool:
    """Validate that string is not None or empty."""
    return bool(value and value.strip())


def validate_positive_number(value: float) -> bool:
    """Validate that number is positive."""
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False
