"""
Utility functions for input sanitization to prevent XSS attacks.
"""
import html
import re


def sanitize_for_output(text: str) -> str:
    """
    Sanitize user input before including it in responses to prevent XSS.
    
    This function:
    1. HTML-escapes special characters
    2. Removes potentially dangerous characters
    
    Args:
        text: The user input to sanitize
        
    Returns:
        Sanitized string safe for output
    """
    if not text or not isinstance(text, str):
        return ""
    
    # HTML escape to prevent script injection
    sanitized = html.escape(text, quote=True)
    
    # Remove null bytes and control characters except newlines/tabs
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
    
    return sanitized
