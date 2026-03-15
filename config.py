import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/adms_expense'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Verify connections before using
    }
    
    # Flask-Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/adms_expense_dev'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/adms_expense_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/adms_expense'
    
    # Production-specific connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 20)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 40)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10
        }
    }

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
