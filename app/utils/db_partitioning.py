from flask import current_app
from app import db
import logging

def setup_database_partitions():
    """
    Setup database partitions for performance optimization:
    - Range partitioning for expense and income tables (by date)
    - Hash partitioning for users table (by user_id)
    
    For MySQL: Implements proper table partitioning
    For SQLite: Creates indexes to simulate partitioning
    """
    try:
        database_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # Check if using SQLite
        if 'sqlite' in database_uri:
            # Create indexes to simulate partitioning
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses (date)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses (user_id)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_incomes_date ON incomes (date)'))
            db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_incomes_user_id ON incomes (user_id)'))
            db.session.commit()
            current_app.logger.info("SQLite indexes created to simulate partitioning")
            
        elif 'mysql' in database_uri:
            # MySQL: Setup proper table partitioning
            try:
                # Get raw connection for MySQL-specific operations
                connection = db.engine.raw_connection()
                cursor = connection.cursor()
                
                # Setup partitions for each table
                setup_expense_partitions(cursor)
                setup_income_partitions(cursor)
                setup_user_partitions(cursor)
                
                connection.commit()
                cursor.close()
                connection.close()
                
                current_app.logger.info("MySQL partitioning setup completed")
                
            except Exception as e:
                current_app.logger.warning(f"MySQL partitioning failed: {str(e)}")
                # Create regular indexes as fallback
                db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses (date)'))
                db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses (user_id)'))
                db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_incomes_date ON incomes (date)'))
                db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_incomes_user_id ON incomes (user_id)'))
                db.session.commit()
                current_app.logger.info("MySQL indexes created as partitioning fallback")
        else:
            current_app.logger.info("Database partitioning not implemented for this database type")
            
    except Exception as e:
        current_app.logger.error(f"Error setting up database partitions: {str(e)}")
        # Don't raise the exception, just log it
        pass

def setup_expense_partitions(cursor):
    """
    Setup RANGE partitioning for expenses table by date
    This divides expenses into quarterly partitions for efficient date-based queries
    """
    try:
        # First, check if the table is already partitioned
        cursor.execute("SELECT PARTITION_NAME FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = 'expenses'")
        if cursor.fetchone():
            current_app.logger.info("Expenses table is already partitioned")
            return
            
        # Create partitioning by range on date column
        partition_sql = """
        ALTER TABLE expenses
        PARTITION BY RANGE (YEAR(date) * 100 + MONTH(date)) (
            PARTITION p202301 VALUES LESS THAN (202304),
            PARTITION p202304 VALUES LESS THAN (202307),
            PARTITION p202307 VALUES LESS THAN (202310),
            PARTITION p202310 VALUES LESS THAN (202401),
            PARTITION p202401 VALUES LESS THAN (202404),
            PARTITION p202404 VALUES LESS THAN (202407),
            PARTITION p202407 VALUES LESS THAN (202410),
            PARTITION p202410 VALUES LESS THAN (202501),
            PARTITION p202501 VALUES LESS THAN (202504),
            PARTITION p202504 VALUES LESS THAN (202507),
            PARTITION p202507 VALUES LESS THAN (202510),
            PARTITION p202510 VALUES LESS THAN (202601),
            PARTITION pmax VALUES LESS THAN MAXVALUE
        )
        """
        cursor.execute(partition_sql)
        current_app.logger.info("Range partitioning applied to expenses table")
    except Exception as e:
        current_app.logger.error(f"Error setting up expense partitions: {str(e)}")
        # Continue execution even if partitioning fails
        pass

def setup_income_partitions(cursor):
    """
    Setup RANGE partitioning for incomes table by date
    This divides incomes into quarterly partitions for efficient date-based queries
    """
    try:
        # First, check if the table is already partitioned
        cursor.execute("SELECT PARTITION_NAME FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = 'incomes'")
        if cursor.fetchone():
            current_app.logger.info("Incomes table is already partitioned")
            return
            
        # Create partitioning by range on date column
        partition_sql = """
        ALTER TABLE incomes
        PARTITION BY RANGE (YEAR(date) * 100 + MONTH(date)) (
            PARTITION p202301 VALUES LESS THAN (202304),
            PARTITION p202304 VALUES LESS THAN (202307),
            PARTITION p202307 VALUES LESS THAN (202310),
            PARTITION p202310 VALUES LESS THAN (202401),
            PARTITION p202401 VALUES LESS THAN (202404),
            PARTITION p202404 VALUES LESS THAN (202407),
            PARTITION p202407 VALUES LESS THAN (202410),
            PARTITION p202410 VALUES LESS THAN (202501),
            PARTITION p202501 VALUES LESS THAN (202504),
            PARTITION p202504 VALUES LESS THAN (202507),
            PARTITION p202507 VALUES LESS THAN (202510),
            PARTITION p202510 VALUES LESS THAN (202601),
            PARTITION pmax VALUES LESS THAN MAXVALUE
        )
        """
        cursor.execute(partition_sql)
        current_app.logger.info("Range partitioning applied to incomes table")
    except Exception as e:
        current_app.logger.error(f"Error setting up income partitions: {str(e)}")
        # Continue execution even if partitioning fails
        pass

def setup_user_partitions(cursor):
    """
    Setup HASH partitioning for users table by user_id
    This distributes users evenly across partitions for load balancing
    """
    try:
        # First, check if the table is already partitioned
        cursor.execute("SELECT PARTITION_NAME FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = 'users'")
        if cursor.fetchone():
            current_app.logger.info("Users table is already partitioned")
            return
            
        # Create partitioning by hash on user_id column (4 partitions)
        partition_sql = """
        ALTER TABLE users
        PARTITION BY HASH(id)
        PARTITIONS 4
        """
        cursor.execute(partition_sql)
        current_app.logger.info("Hash partitioning applied to users table")
    except Exception as e:
        current_app.logger.error(f"Error setting up user partitions: {str(e)}")
        # Continue execution even if partitioning fails
        pass
