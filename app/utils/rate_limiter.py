"""
Simple rate limiting middleware using in-memory storage
"""
from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# In-memory storage for rate limiting (use Redis in production)
request_counts = {}
blocked_ips = {}

class RateLimiter:
    """Simple rate limiter class"""
    
    def __init__(self, max_requests=100, window_seconds=60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_rate_limited(self, identifier):
        """Check if identifier is rate limited"""
        now = datetime.utcnow()
        
        # Check if IP is permanently blocked
        if identifier in blocked_ips:
            block_until = blocked_ips[identifier]
            if now < block_until:
                return True
            else:
                del blocked_ips[identifier]
        
        # Initialize tracking for new identifiers
        if identifier not in request_counts:
            request_counts[identifier] = []
        
        # Remove old requests outside the window
        window_start = now - timedelta(seconds=self.window_seconds)
        request_counts[identifier] = [
            req_time for req_time in request_counts[identifier]
            if req_time > window_start
        ]
        
        # Check if over limit
        if len(request_counts[identifier]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return True
        
        # Add current request
        request_counts[identifier].append(now)
        return False
    
    def block_ip(self, identifier, duration_minutes=60):
        """Block an IP for a specific duration"""
        blocked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        blocked_ips[identifier] = blocked_until
        logger.warning(f"Blocked {identifier} until {blocked_until}")

def rate_limit(max_requests=100, window_seconds=60):
    """
    Decorator for rate limiting endpoints
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as identifier
            identifier = request.remote_addr
            
            if limiter.is_rate_limited(identifier):
                logger.warning(f"Rate limit hit for {identifier} on {request.path}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def init_rate_limiting(app):
    """Initialize rate limiting for the application"""
    
    @app.before_request
    def check_rate_limit():
        """Global rate limiting check"""
        # Skip rate limiting for static files
        if request.path.startswith('/static/'):
            return None
        
        # Apply stricter limits for login attempts
        if request.path.endswith('/login') and request.method == 'POST':
            limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
            if limiter.is_rate_limited(request.remote_addr):
                return jsonify({
                    'error': 'Too many login attempts',
                    'message': 'Please try again later.'
                }), 429
        
        return None
    
    logger.info("Rate limiting initialized")
