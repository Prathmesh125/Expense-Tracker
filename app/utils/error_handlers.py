"""
Error handlers for the application
"""
from flask import render_template, jsonify, request
from app import db
import logging

logger = logging.getLogger(__name__)

def init_error_handlers(app):
    """Initialize error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        logger.warning(f"404 error: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"500 error: {str(error)}", exc_info=True)
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        logger.warning(f"403 error: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors"""
        logger.warning(f"400 error: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad request'}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all uncaught exceptions"""
        logger.error(f"Uncaught exception: {str(error)}", exc_info=True)
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
