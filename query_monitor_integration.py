"""
Flask app integration with real-time query monitoring
Add this to your run.py to enable query monitoring
"""

from query_monitor import configure_flask_app

def setup_query_monitoring(app):
    """
    Setup query monitoring for the Flask application
    
    Args:
        app: Flask application instance
    
    Returns:
        monitor: The query monitor instance
    """
    # Configure Flask app with query monitoring
    monitor, _ = configure_flask_app(app, use_sqlite=True)
    
    # Return the monitor instance in case it's needed elsewhere
    return monitor

# Example usage in run.py:
"""
import os
from app import create_app
from flask_migrate import Migrate
from app.models import db, User, Expense, Category, Income
from query_monitor_integration import setup_query_monitoring

app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)

# Setup query monitoring
monitor = setup_query_monitoring(app)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5003, help='Port to run the application on')
    parser.add_argument('--monitor', action='store_true', help='Enable query monitoring display')
    args = parser.parse_args()
    
    # If monitoring display is enabled, start it in a separate thread
    if args.monitor and monitor:
        import threading
        threading.Thread(target=monitor.display_live_monitor, daemon=True).start()
    
    app.run(host='0.0.0.0', port=args.port, debug=True)
"""
