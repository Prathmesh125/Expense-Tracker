"""
Input sanitization utilities to prevent XSS and injection attacks
"""
import re
import html
from urllib.parse import urlparse

def sanitize_html(text):
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        Escaped HTML string
    """
    if not text:
        return ""
    
    # Escape HTML special characters
    sanitized = html.escape(str(text))
    return sanitized

def sanitize_sql_identifier(identifier):
    """
    Sanitize SQL identifier (table name, column name)
    
    Args:
        identifier: SQL identifier
        
    Returns:
        Sanitized identifier or None if invalid
    """
    if not identifier:
        return None
    
    # Allow only alphanumeric and underscore
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        return identifier
    
    return None

def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove path separators
    sanitized = str(filename).replace('/', '').replace('\\', '')
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip('.')
    
    # Allow only safe characters
    sanitized = re.sub(r'[^\w\s.-]', '', sanitized)
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized or "unnamed"

def sanitize_url(url):
    """
    Sanitize URL to prevent malicious redirects
    
    Args:
        url: URL string
        
    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        
        # Allow only http and https schemes
        if parsed.scheme not in ['http', 'https', '']:
            return None
        
        # Prevent javascript: and data: URLs
        if parsed.scheme in ['javascript', 'data', 'vbscript']:
            return None
        
        return url
    except Exception:
        return None

def remove_control_characters(text):
    """
    Remove control characters from text
    
    Args:
        text: Input text
        
    Returns:
        Text with control characters removed
    """
    if not text:
        return ""
    
    # Remove control characters except newline, tab, and carriage return
    return ''.join(char for char in str(text) if ord(char) >= 32 or char in '\n\t\r')

def sanitize_email(email):
    """
    Sanitize email address
    
    Args:
        email: Email address
        
    Returns:
        Sanitized email or None if invalid
    """
    if not email:
        return None
    
    # Convert to lowercase and strip whitespace
    sanitized = str(email).lower().strip()
    
    # Check basic format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sanitized):
        return None
    
    return sanitized

def sanitize_phone(phone):
    """
    Sanitize phone number
    
    Args:
        phone: Phone number
        
    Returns:
        Sanitized phone number with only digits and common separators
    """
    if not phone:
        return ""
    
    # Keep only digits, spaces, dashes, parentheses, and plus
    sanitized = re.sub(r'[^\d\s\-\(\)\+]', '', str(phone))
    
    return sanitized.strip()

def strip_tags(text):
    """
    Remove all HTML tags from text
    
    Args:
        text: Text with HTML tags
        
    Returns:
        Plain text without HTML tags
    """
    if not text:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', str(text))
    
    # Decode HTML entities
    clean = html.unescape(clean)
    
    return clean.strip()

def sanitize_search_query(query):
    """
    Sanitize search query to prevent injection attacks
    
    Args:
        query: Search query
        
    Returns:
        Sanitized search query
    """
    if not query:
        return ""
    
    # Remove control characters
    sanitized = remove_control_characters(query)
    
    # Remove special characters that could be used in attacks
    sanitized = re.sub(r'[<>\"\'%;()&+]', '', sanitized)
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized.strip()

def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
