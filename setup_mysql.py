#!/usr/bin/env python3
"""
MySQL Database Setup Script for ADMS Expense Tracker
This script helps set up MySQL databases and test connections
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import getpass

def test_mysql_connection(host, user, password):
    """Test MySQL connection"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if connection.is_connected():
            return True, connection
    except Error as e:
        return False, str(e)

def create_databases(connection, databases):
    """Create databases if they don't exist"""
    cursor = connection.cursor()
    
    for db_name in databases:
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{db_name}' created successfully")
        except Error as e:
            print(f"❌ Error creating database '{db_name}': {e}")
    
    cursor.close()

def update_env_file(user, password):
    """Update .env file with database URLs"""
    env_content = f"""# Flask application environment variables
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# MySQL Database configuration
DATABASE_URL=mysql+pymysql://{user}:{password}@localhost/adms_expense
DEV_DATABASE_URL=mysql+pymysql://{user}:{password}@localhost/adms_expense_dev
TEST_DATABASE_URL=mysql+pymysql://{user}:{password}@localhost/adms_expense_test

# Mail server settings (optional)
# MAIL_SERVER=smtp.example.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your_email@example.com
# MAIL_PASSWORD=your_password

# Admin email
# ADMIN_EMAIL=admin@example.com
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file updated successfully")
        return True
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def main():
    print("MySQL Database Setup for ADMS Expense Tracker")
    print("=" * 50)
    print()
    
    # Get MySQL credentials
    host = input("Enter MySQL host (default: localhost): ").strip() or "localhost"
    user = input("Enter MySQL username (default: root): ").strip() or "root"
    password = getpass.getpass("Enter MySQL password: ")
    
    print("\n🔗 Testing MySQL connection...")
    
    # Test connection
    connected, connection = test_mysql_connection(host, user, password)
    
    if not connected:
        print(f"❌ Failed to connect to MySQL: {connection}")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. Username and password are correct")
        print("3. User has necessary permissions")
        sys.exit(1)
    
    print("✅ MySQL connection successful")
    
    # Create databases
    databases = [
        'adms_expense',
        'adms_expense_dev', 
        'adms_expense_test'
    ]
    
    print(f"\n📊 Creating databases...")
    create_databases(connection, databases)
    
    # Ask to update .env file
    update_env = input("\n🤔 Update .env file with database URLs? (y/N): ").strip().lower()
    
    if update_env in ['y', 'yes']:
        if update_env_file(user, password):
            print("✅ Configuration updated successfully!")
        else:
            print("⚠️  Please manually update the .env file with your database URLs")
    else:
        print("\n📝 Please manually update your .env file with:")
        print(f"DATABASE_URL=mysql+pymysql://{user}:YOUR_PASSWORD@{host}/adms_expense")
        print(f"DEV_DATABASE_URL=mysql+pymysql://{user}:YOUR_PASSWORD@{host}/adms_expense_dev")
        print(f"TEST_DATABASE_URL=mysql+pymysql://{user}:YOUR_PASSWORD@{host}/adms_expense_test")
    
    connection.close()
    
    print(f"\n🚀 Next steps:")
    print("1. Make sure your .env file has the correct MySQL credentials")
    print("2. Run: source venv/bin/activate")
    print("3. Run: flask db init (if migrations folder doesn't exist)")
    print("4. Run: flask db migrate -m 'Initial migration to MySQL'")
    print("5. Run: flask db upgrade")
    print("6. Run: flask run")

if __name__ == "__main__":
    main()
