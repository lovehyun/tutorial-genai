# app/utils/validators.py
import re
from typing import Optional

def validate_username(username: str) -> Optional[str]:
    """Validate username format"""
    if len(username) < 3 or len(username) > 50:
        return "Username must be between 3 and 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+', username):
        return "Username can only contain letters, numbers, hyphens, and underscores"
    
    return None

def validate_password(password: str) -> Optional[str]:
    """Validate password strength"""
    if len(password) < 6:
        return "Password must be at least 6 characters long"
    
    if len(password) > 100:
        return "Password must be less than 100 characters"
    
    return None

def validate_model_name(name: str) -> Optional[str]:
    """Validate model name"""
    if len(name) < 1 or len(name) > 100:
        return "Model name must be between 1 and 100 characters"
    
    if not re.match(r'^[a-zA-Z0-9_\-\s\.]+$', name):
        return "Model name contains invalid characters"
    
    return None
