"""
Error handlers for the application
"""
from flask import render_template, jsonify, request
from app import db
import logging

logger = logging.getLogger(__name__)

def init_error_handlers(app):
    """Initialize error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors"""
        logger.warning(f"400 error: {request.url} - {str(error)}")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Bad request',
                'message': 'The request was malformed or invalid. Please check your input and try again.'
            }), 400
        return render_template('errors/400.html', 
                             message='The request was invalid. Please check your input and try again.'), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 errors"""
        logger.warning(f"401 error: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource.'
            }), 401
        return render_template('errors/403.html',
                             message='You must be logged in to access this page.'), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        logger.warning(f"403 error: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource.'
            }), 403
        return render_template('errors/403.html',
                             message='You do not have permission to access this page.'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        logger.warning(f"404 error: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Resource not found',
                'message': 'The requested resource could not be found.'
            }), 404
        return render_template('errors/404.html',
                             message='The page you are looking for does not exist.'), 404
    
    @app.errorhandler(413)
    def request_entity_too_large_error(error):
        """Handle 413 errors"""
        logger.warning(f"413 error: {request.url} - Request too large")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Request too large',
                'message': 'The uploaded file or data is too large. Please reduce the size and try again.'
            }), 413
        return render_template('errors/400.html',
                             message='The file or data you are trying to upload is too large.'), 413
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Handle 429 errors (rate limiting)"""
        logger.warning(f"429 error: {request.url} - Too many requests")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Too many requests',
                'message': 'You have made too many requests. Please wait a moment and try again.'
            }), 429
        return render_template('errors/400.html',
                             message='Too many requests. Please wait a moment before trying again.'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"500 error: {str(error)}", exc_info=True)
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred. Our team has been notified.'
            }), 500
        return render_template('errors/500.html',
                             message='An unexpected error occurred. Please try again later.'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all uncaught exceptions"""
        logger.error(f"Uncaught exception: {str(error)}", exc_info=True)
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'An unexpected error occurred',
                'message': 'Something went wrong. Our team has been notified.'
            }), 500
        return render_template('errors/500.html',
                             message='An unexpected error occurred. Please try again later.'), 500
