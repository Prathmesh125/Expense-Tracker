"""
Validation utilities for input data
"""
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None

def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 64:
        return False, "Username must not exceed 64 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None

def validate_amount(amount):
    """Validate monetary amount"""
    if amount is None:
        return False, "Amount is required"
    
    try:
        decimal_amount = Decimal(str(amount))
        if decimal_amount <= 0:
            return False, "Amount must be greater than zero"
        
        if decimal_amount > Decimal('999999999.99'):
            return False, "Amount is too large"
        
        return True, None
    except (InvalidOperation, ValueError, TypeError):
        return False, "Invalid amount format"

def validate_date(date_str, date_format='%Y-%m-%d'):
    """Validate date format"""
    if not date_str:
        return False, "Date is required"
    
    try:
        if isinstance(date_str, date):
            return True, None
        
        parsed_date = datetime.strptime(str(date_str), date_format)
        
        # Check if date is not in the future
        if parsed_date.date() > date.today():
            return False, "Date cannot be in the future"
        
        return True, None
    except ValueError:
        return False, f"Invalid date format. Expected format: {date_format}"

def validate_category_name(name):
    """Validate category name"""
    if not name:
        return False, "Category name is required"
    
    if len(name) < 2:
        return False, "Category name must be at least 2 characters long"
    
    if len(name) > 64:
        return False, "Category name must not exceed 64 characters"
    
    return True, None

def validate_description(description, max_length=256):
    """Validate description field"""
    if description and len(description) > max_length:
        return False, f"Description must not exceed {max_length} characters"
    
    return True, None

def sanitize_string(text):
    """Sanitize string input"""
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = str(text).strip()
    
    # Remove any null bytes
    sanitized = sanitized.replace('\x00', '')
    
    return sanitized

def validate_positive_integer(value):
    """Validate positive integer"""
    try:
        int_value = int(value)
        if int_value <= 0:
            return False, "Value must be a positive integer"
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid integer value"
