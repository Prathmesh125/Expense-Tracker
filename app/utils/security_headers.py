"""
Security headers middleware to protect against common web vulnerabilities
"""
from flask import request
import logging

logger = logging.getLogger(__name__)

def init_security_headers(app):
    """Initialize security headers for the application"""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to every response"""
        
        # Prevent clickjacking attacks
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS filtering in browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Enforce HTTPS (uncomment in production with HTTPS)
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdn.plot.ly; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=()'
        )
        
        return response
    
    @app.after_request
    def remove_server_header(response):
        """Remove server header to avoid information disclosure"""
        response.headers.pop('Server', None)
        return response
    
    @app.before_request
    def check_secure_requests():
        """Check for secure requests in production"""
        if app.config.get('ENV') == 'production':
            # In production, enforce HTTPS
            if not request.is_secure and request.headers.get('X-Forwarded-Proto', 'http') != 'https':
                # Skip for health check endpoint
                if request.path == '/health':
                    return None
                logger.warning(f"Insecure request to {request.path} from {request.remote_addr}")
        
        return None
    
    logger.info("Security headers initialized")
