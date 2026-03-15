"""
Logging configuration for the application
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set logging level based on environment
    if app.config.get('DEBUG'):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Configure file handler for general logs
    file_handler = RotatingFileHandler(
        'logs/adms_expense.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    # Configure file handler for errors
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    error_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_handler)
    
    # Set overall logger level
    app.logger.setLevel(log_level)
    
    # Log application startup
    app.logger.info('ADMS Expense Tracker startup')
    app.logger.info(f'Logging level: {logging.getLevelName(log_level)}')
    app.logger.info(f'Environment: {app.config.get("ENV", "unknown")}')
    
    return app

def log_request(request, response=None):
    """Log HTTP request details"""
    logger = logging.getLogger(__name__)
    log_message = f'{request.method} {request.path} - {request.remote_addr}'
    if response:
        log_message += f' - {response.status_code}'
    logger.info(log_message)

def log_database_query(query, duration=None):
    """Log database query execution"""
    logger = logging.getLogger(__name__)
    log_message = f'DB Query: {query}'
    if duration:
        log_message += f' (Duration: {duration:.3f}s)'
    logger.debug(log_message)
