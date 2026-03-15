import hashlib
import uuid
from datetime import datetime

def generate_password_hash(password):
    """
    Generate a secure hash for a password using SHA-256
    
    Args:
        password (str): The password to hash
        
    Returns:
        str: The hashed password
    """
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def verify_password_hash(hashed_password, password):
    """
    Verify a password against its hash
    
    Args:
        hashed_password (str): The stored hash
        password (str): The password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    password_hash, salt = hashed_password.split(':')
    return password_hash == hashlib.sha256(salt.encode() + password.encode()).hexdigest()

def generate_transaction_hash(user_id, amount, date, description):
    """
    Generate a hash for a transaction to detect duplicates
    
    Args:
        user_id (int): User ID
        amount (float): Transaction amount
        date (datetime): Transaction date
        description (str): Transaction description
        
    Returns:
        str: Transaction hash
    """
    # Format date as string if it's a datetime object
    date_str = date.strftime('%Y-%m-%d') if isinstance(date, datetime) else str(date)
    
    # Create a string with all transaction details
    content = f"{user_id}-{amount}-{date_str}-{description}"
    
    # Generate MD5 hash (sufficient for duplicate detection)
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def consistent_hash(key, bucket_count):
    """
    Implement consistent hashing for data distribution
    
    Args:
        key (str): The key to hash
        bucket_count (int): Number of buckets
        
    Returns:
        int: Bucket number for this key
    """
    # Convert key to bytes if it's a string
    if isinstance(key, str):
        key = key.encode('utf-8')
        
    # Generate a hash value
    hash_val = int(hashlib.md5(key).hexdigest(), 16)
    
    # Map to bucket number
    return hash_val % bucket_count
