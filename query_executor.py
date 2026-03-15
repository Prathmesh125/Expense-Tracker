#!/usr/bin/env python3
"""
MySQL Query Executor for ADMS Expense Tracker
Interactive tool to execute SQL queries on the database
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
import getpass
from datetime import datetime
import json

class MySQLQueryExecutor:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.config = {}
    
    def load_config_from_env(self):
        """Load database configuration from .env file"""
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if 'DEV_DATABASE_URL' in key:
                            # Parse MySQL URL: mysql+pymysql://user:password@host/database
                            if 'mysql+pymysql://' in value:
                                url = value.replace('mysql+pymysql://', '')
                                if '@' in url:
                                    auth, host_db = url.split('@')
                                    if ':' in auth:
                                        user, password = auth.split(':', 1)
                                    else:
                                        user, password = auth, ''
                                    
                                    if '/' in host_db:
                                        host, database = host_db.split('/', 1)
                                    else:
                                        host, database = host_db, ''
                                    
                                    self.config = {
                                        'host': host,
                                        'user': user,
                                        'password': password,
                                        'database': database
                                    }
                                    return True
        except FileNotFoundError:
            print("⚠️  .env file not found")
        return False
    
    def get_manual_config(self):
        """Get database configuration manually from user"""
        print("🔧 Database Configuration")
        print("-" * 25)
        
        self.config['host'] = input("Host (default: localhost): ").strip() or 'localhost'
        self.config['user'] = input("Username (default: root): ").strip() or 'root'
        self.config['password'] = getpass.getpass("Password: ")
        self.config['database'] = input("Database (default: adms_expense_dev): ").strip() or 'adms_expense_dev'
    
    def connect(self):
        """Connect to MySQL database"""
        if not self.config:
            if not self.load_config_from_env():
                self.get_manual_config()
        
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to MySQL database: {self.config['database']}")
            return True
        except Error as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return results"""
        if not self.connection or not self.cursor:
            print("❌ No database connection")
            return None
        
        try:
            query = query.strip()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # For SELECT queries, fetch results
            if query.upper().startswith('SELECT') or query.upper().startswith('SHOW') or query.upper().startswith('DESCRIBE'):
                results = self.cursor.fetchall()
                columns = [desc[0] for desc in self.cursor.description]
                return {
                    'type': 'select',
                    'columns': columns,
                    'data': results,
                    'count': len(results)
                }
            else:
                # For INSERT, UPDATE, DELETE, etc.
                self.connection.commit()
                return {
                    'type': 'modify',
                    'affected_rows': self.cursor.rowcount,
                    'message': f"Query executed successfully. {self.cursor.rowcount} rows affected."
                }
                
        except Error as e:
            print(f"❌ Query execution failed: {e}")
            return None
    
    def display_results(self, result):
        """Display query results in a formatted table"""
        if not result:
            return
        
        if result['type'] == 'select':
            if result['count'] == 0:
                print("📭 No results found")
                return
            
            print(f"\n📊 Results ({result['count']} rows):")
            print("=" * 50)
            
            # Use tabulate for nice table formatting
            try:
                table = tabulate(result['data'], headers=result['columns'], tablefmt='grid')
                print(table)
            except:
                # Fallback to simple formatting
                print(" | ".join(result['columns']))
                print("-" * (len(" | ".join(result['columns']))))
                for row in result['data']:
                    print(" | ".join(str(col) for col in row))
        
        elif result['type'] == 'modify':
            print(f"✅ {result['message']}")
    
    def run_predefined_queries(self):
        """Run some predefined useful queries"""
        queries = {
            "1": {
                "name": "Show all tables",
                "query": "SHOW TABLES"
            },
            "2": {
                "name": "Count records in all tables",
                "query": """
                SELECT 
                    'users' as table_name, COUNT(*) as record_count FROM users
                UNION ALL
                SELECT 'categories', COUNT(*) FROM categories
                UNION ALL
                SELECT 'expenses', COUNT(*) FROM expenses
                UNION ALL
                SELECT 'incomes', COUNT(*) FROM incomes
                UNION ALL
                SELECT 'budgets', COUNT(*) FROM budgets
                """
            },
            "3": {
                "name": "Recent expenses (last 10)",
                "query": "SELECT e.id, e.amount, e.description, e.date, c.name as category, u.username FROM expenses e LEFT JOIN categories c ON e.category_id = c.id LEFT JOIN users u ON e.user_id = u.id ORDER BY e.date DESC LIMIT 10"
            },
            "4": {
                "name": "Recent incomes (last 10)",
                "query": "SELECT i.id, i.amount, i.source, i.description, i.date, u.username FROM incomes i LEFT JOIN users u ON i.user_id = u.id ORDER BY i.date DESC LIMIT 10"
            },
            "5": {
                "name": "Users overview",
                "query": "SELECT id, username, email, first_name, last_name, created_at FROM users"
            },
            "6": {
                "name": "Categories with expense counts",
                "query": "SELECT c.id, c.name, c.description, COUNT(e.id) as expense_count, u.username FROM categories c LEFT JOIN expenses e ON c.id = e.category_id LEFT JOIN users u ON c.user_id = u.id GROUP BY c.id, c.name, c.description, u.username ORDER BY expense_count DESC"
            },
            "7": {
                "name": "Monthly expense summary (current year)",
                "query": "SELECT YEAR(date) as year, MONTH(date) as month, COUNT(*) as expense_count, SUM(amount) as total_amount FROM expenses WHERE YEAR(date) = YEAR(CURDATE()) GROUP BY YEAR(date), MONTH(date) ORDER BY year, month"
            },
            "8": {
                "name": "Show partition information",
                "query": "SELECT TABLE_NAME, PARTITION_NAME, PARTITION_METHOD, PARTITION_EXPRESSION, TABLE_ROWS FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_SCHEMA = DATABASE() AND PARTITION_NAME IS NOT NULL ORDER BY TABLE_NAME, PARTITION_NAME"
            },
            "9": {
                "name": "Database schema overview",
                "query": "SELECT TABLE_NAME, ENGINE, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() ORDER BY TABLE_NAME"
            }
        }
        
        while True:
            print("\n🔍 Predefined Queries")
            print("=" * 30)
            for key, query_info in queries.items():
                print(f"{key}. {query_info['name']}")
            print("0. Return to main menu")
            
            choice = input("\nSelect query (0-9): ").strip()
            
            if choice == "0":
                break
            elif choice in queries:
                print(f"\n🚀 Executing: {queries[choice]['name']}")
                print(f"📝 Query: {queries[choice]['query']}")
                result = self.execute_query(queries[choice]['query'])
                self.display_results(result)
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice")
    
    def interactive_mode(self):
        """Interactive query execution mode"""
        print("\n💻 Interactive Query Mode")
        print("=" * 30)
        print("Type your SQL queries (type 'exit' to quit, 'help' for commands)")
        print()
        
        while True:
            try:
                query = input("SQL> ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                elif query.lower() == 'help':
                    print("\n📚 Available Commands:")
                    print("  help     - Show this help")
                    print("  exit/quit/q - Exit interactive mode")
                    print("  clear    - Clear screen")
                    print("  tables   - Show all tables")
                    print("  desc <table> - Describe table structure")
                    print("\n💡 Examples:")
                    print("  SELECT * FROM users;")
                    print("  SELECT * FROM expenses WHERE date >= '2025-08-01';")
                    print("  UPDATE users SET first_name = 'John' WHERE id = 1;")
                    continue
                elif query.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif query.lower() == 'tables':
                    query = "SHOW TABLES"
                elif query.lower().startswith('desc '):
                    table_name = query[5:].strip()
                    query = f"DESCRIBE {table_name}"
                elif not query:
                    continue
                
                print(f"\n🚀 Executing query...")
                result = self.execute_query(query)
                self.display_results(result)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                break
    
    def export_results(self, query, filename=None):
        """Export query results to JSON file"""
        result = self.execute_query(query)
        if not result or result['type'] != 'select':
            print("❌ No data to export")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_results_{timestamp}.json"
        
        export_data = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'columns': result['columns'],
            'data': result['data'],
            'count': result['count']
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"✅ Results exported to: {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Database connection closed")

def main():
    print("🐬 MySQL Query Executor for ADMS Expense Tracker")
    print("=" * 55)
    
    executor = MySQLQueryExecutor()
    
    if not executor.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        while True:
            print("\n🎯 Main Menu")
            print("-" * 20)
            print("1. Predefined queries")
            print("2. Interactive query mode")
            print("3. Execute single query")
            print("4. Export query results")
            print("0. Exit")
            
            choice = input("\nSelect option (0-4): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                executor.run_predefined_queries()
            elif choice == "2":
                executor.interactive_mode()
            elif choice == "3":
                query = input("\nEnter SQL query: ").strip()
                if query:
                    result = executor.execute_query(query)
                    executor.display_results(result)
                    input("\nPress Enter to continue...")
            elif choice == "4":
                query = input("\nEnter SQL query to export: ").strip()
                filename = input("Export filename (optional): ").strip() or None
                if query:
                    executor.export_results(query, filename)
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        executor.close()

if __name__ == "__main__":
    main()
