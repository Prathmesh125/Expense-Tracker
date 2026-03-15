#!/usr/bin/env python3
"""
Simple MySQL Query Tool - No external dependencies
Quick and simple SQL query executor for ADMS Expense Tracker
"""

import os
import mysql.connector
from mysql.connector import Error
import getpass

def connect_to_db():
    """Connect to MySQL database using .env configuration"""
    config = {}
    
    # Try to read from .env file
    try:
        with open('.env', 'r') as f:
            for line in f:
                if 'DEV_DATABASE_URL=' in line and not line.strip().startswith('#'):
                    url = line.split('=', 1)[1].strip()
                    if 'mysql+pymysql://' in url:
                        url = url.replace('mysql+pymysql://', '')
                        if '@' in url:
                            auth, host_db = url.split('@')
                            user, password = auth.split(':', 1) if ':' in auth else (auth, '')
                            host, database = host_db.split('/', 1) if '/' in host_db else (host_db, '')
                            
                            config = {
                                'host': host,
                                'user': user,
                                'password': password,
                                'database': database
                            }
                            break
    except FileNotFoundError:
        pass
    
    # Manual input if .env not found
    if not config:
        print("🔧 Enter Database Configuration:")
        config = {
            'host': input("Host (localhost): ").strip() or 'localhost',
            'user': input("Username (root): ").strip() or 'root',
            'password': getpass.getpass("Password: "),
            'database': input("Database (adms_expense_dev): ").strip() or 'adms_expense_dev'
        }
    
    try:
        connection = mysql.connector.connect(**config)
        print(f"✅ Connected to database: {config['database']}")
        return connection
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return None

def execute_query(connection, query):
    """Execute SQL query and display results"""
    cursor = connection.cursor()
    
    try:
        cursor.execute(query)
        
        # Check if it's a SELECT query
        if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            if not results:
                print("📭 No results found")
                return
            
            # Display results
            print(f"\n📊 Results ({len(results)} rows):")
            print("=" * 60)
            
            # Print headers
            print(" | ".join(f"{col:15}" for col in columns))
            print("-" * (len(columns) * 18))
            
            # Print rows
            for row in results:
                print(" | ".join(f"{str(col)[:15]:15}" for col in row))
        else:
            # For INSERT, UPDATE, DELETE, etc.
            connection.commit()
            print(f"✅ Query executed successfully. {cursor.rowcount} rows affected.")
    
    except Error as e:
        print(f"❌ Query failed: {e}")
    finally:
        cursor.close()

def quick_queries_menu(connection):
    """Show menu of quick queries"""
    queries = {
        '1': ('Show all tables', 'SHOW TABLES'),
        '2': ('Count all records', '''
            SELECT 'users' as table_name, COUNT(*) as count FROM users
            UNION ALL SELECT 'expenses', COUNT(*) FROM expenses
            UNION ALL SELECT 'incomes', COUNT(*) FROM incomes
            UNION ALL SELECT 'categories', COUNT(*) FROM categories
        '''),
        '3': ('Recent expenses', 'SELECT * FROM expenses ORDER BY date DESC LIMIT 10'),
        '4': ('Recent incomes', 'SELECT * FROM incomes ORDER BY date DESC LIMIT 10'),
        '5': ('All users', 'SELECT id, username, email, first_name, last_name FROM users'),
        '6': ('All categories', 'SELECT * FROM categories'),
        '7': ('Expenses with categories', '''
            SELECT e.id, e.amount, e.description, e.date, c.name as category 
            FROM expenses e 
            LEFT JOIN categories c ON e.category_id = c.id 
            ORDER BY e.date DESC LIMIT 10
        '''),
        '8': ('Today\'s expenses', 'SELECT * FROM expenses WHERE date = CURDATE()'),
        '9': ('This month\'s total', '''
            SELECT 
                COUNT(*) as expense_count, 
                SUM(amount) as total_amount 
            FROM expenses 
            WHERE YEAR(date) = YEAR(CURDATE()) 
            AND MONTH(date) = MONTH(CURDATE())
        ''')
    }
    
    while True:
        print("\n🔍 Quick Queries:")
        print("-" * 20)
        for key, (name, _) in queries.items():
            print(f"{key}. {name}")
        print("0. Back to main menu")
        
        choice = input("\nSelect (0-9): ").strip()
        
        if choice == '0':
            break
        elif choice in queries:
            name, query = queries[choice]
            print(f"\n🚀 {name}")
            print(f"📝 {query.strip()}")
            execute_query(connection, query)
            input("\nPress Enter to continue...")
        else:
            print("❌ Invalid choice")

def main():
    print("🐬 Simple MySQL Query Tool")
    print("=" * 35)
    
    connection = connect_to_db()
    if not connection:
        return
    
    try:
        while True:
            print("\n🎯 Options:")
            print("1. Quick queries")
            print("2. Custom query")
            print("0. Exit")
            
            choice = input("\nSelect (0-2): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                quick_queries_menu(connection)
            elif choice == '2':
                query = input("\n📝 Enter SQL query: ").strip()
                if query:
                    execute_query(connection, query)
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        connection.close()
        print("🔌 Connection closed")

if __name__ == "__main__":
    main()
