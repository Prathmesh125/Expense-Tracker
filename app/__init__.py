from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import locale

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Set locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def create_app(config_name):
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register custom filters
    @app.template_filter('format_number')
    def format_number_filter(value):
        try:
            return f"{float(value):,.2f}"
        except (ValueError, TypeError):
            return value
    
    # Register blueprints
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.expense import expense as expense_blueprint
    app.register_blueprint(expense_blueprint, url_prefix='/expense')
    
    from app.routes.income import income as income_blueprint
    app.register_blueprint(income_blueprint, url_prefix='/income')
    
    from app.routes.reports import reports as reports_blueprint
    app.register_blueprint(reports_blueprint)
    
    # Initialize database partitioning
    with app.app_context():
        try:
            db.create_all()  # Create all tables
            from app.utils.db_partitioning import setup_database_partitions
            setup_database_partitions()  # Setup database partitions
            app.logger.info("Database initialized successfully")
        except Exception as e:
            app.logger.error(f"Error initializing database: {str(e)}")
            # Continue with application initialization even if there's a database error
    
    return app
