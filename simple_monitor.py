#!/usr/bin/env python3
"""
Simple Real-time MySQL Database Monitor for Flask Expense Tracker
Monitors MySQL database changes and query patterns in real-time
"""

import pymysql
import time
import os
from datetime import datetime
import json
from threading import Thread
import signal
import sys
from urllib.parse import urlparse

class MySQLDatabaseMonitor:
    def __init__(self, db_config=None):
        if db_config is None:
            # Try to get config from environment or use defaults
            self.db_config = {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'user': os.environ.get('DB_USER', 'root'),
                'password': os.environ.get('DB_PASSWORD', ''),
                'database': os.environ.get('DB_NAME', 'adms_expense_dev'),
                'port': int(os.environ.get('DB_PORT', 3306)),
                'charset': 'utf8mb4'
            }
        else:
            self.db_config = db_config
            
        self.monitoring = False
        self.last_counts = {}
        self.query_log = []
        
    def parse_database_url(self, url):
        """Parse DATABASE_URL into connection parameters"""
        parsed = urlparse(url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:] if parsed.path else 'adms_expense_dev',
            'charset': 'utf8mb4'
        }
    
    def get_connection(self):
        """Get MySQL database connection"""
        try:
            return pymysql.connect(**self.db_config)
        except Exception as e:
            print(f"❌ Error connecting to MySQL: {e}")
            print(f"🔧 Connection config: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
            return None
        
    def get_table_counts(self):
        """Get current row counts for all tables"""
        conn = self.get_connection()
        if not conn:
            return {}
            
        try:
            cursor = conn.cursor()
            
            # Get all table names from the database
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_type = 'BASE TABLE'
            """, (self.db_config['database'],))
            
            tables = [row[0] for row in cursor.fetchall()]
            
            counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                counts[table] = cursor.fetchone()[0]
            
            conn.close()
            return counts
        except Exception as e:
            print(f"❌ Error getting table counts: {e}")
            if conn:
                conn.close()
            return {}
    
    def get_recent_records(self, table, limit=5):
        """Get recent records from a table"""
        conn = self.get_connection()
        if not conn:
            return [], []
            
        try:
            cursor = conn.cursor()
            
            # Get column information for this table
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s 
                ORDER BY ordinal_position
            """, (self.db_config['database'], table))
            
            column_info = cursor.fetchall()
            columns = [col[0] for col in column_info]
            
            # Try to order by common timestamp/id columns
            order_columns = ['id', 'created_at', 'date', 'updated_at']
            order_by = None
            
            for col in order_columns:
                if col in columns:
                    order_by = col
                    break
            
            if order_by:
                cursor.execute(f"SELECT * FROM `{table}` ORDER BY `{order_by}` DESC LIMIT %s", (limit,))
            else:
                cursor.execute(f"SELECT * FROM `{table}` LIMIT %s", (limit,))
            
            records = cursor.fetchall()
            conn.close()
            return records, columns
            
        except Exception as e:
            print(f"❌ Error getting recent records from {table}: {e}")
            if conn:
                conn.close()
            return [], []
    
    def format_record(self, record, columns):
        """Format a database record for display"""
        formatted = {}
        for i, value in enumerate(record):
            if i < len(columns):
                formatted[columns[i]] = value
        return formatted
    
    def monitor_changes(self):
        """Monitor database for changes"""
        print("🔍 Starting database monitoring...")
        print(f"📁 Database: {self.db_config['database']} on {self.db_config['host']}")
        print("💡 Tracking: INSERT, UPDATE, DELETE operations only")
        print("="*60)
        
        # Get initial counts
        self.last_counts = self.get_table_counts()
        print("📊 Initial table counts:")
        for table, count in self.last_counts.items():
            print(f"  {table}: {count} records")
        print()
        
        while self.monitoring:
            time.sleep(2)  # Check every 2 seconds
            
            current_counts = self.get_table_counts()
            
            # Check for changes
            for table, current_count in current_counts.items():
                last_count = self.last_counts.get(table, 0)
                
                if current_count != last_count:
                    change = current_count - last_count
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if change > 0:
                        print(f"🆕 [{timestamp}] NEW RECORD(S) in {table.upper()}")
                        print(f"   Count: {last_count} → {current_count} (+{change})")
                        
                        # Show recent records
                        records, columns = self.get_recent_records(table, abs(change))
                        for record in records:
                            formatted = self.format_record(record, columns)
                            print(f"   📝 New: {json.dumps(formatted, indent=6, default=str)}")
                        print()
                    
                    elif change < 0:
                        print(f"🗑️  [{timestamp}] RECORD(S) DELETED from {table.upper()}")
                        print(f"   Count: {last_count} → {current_count} ({change})")
                        print()
                    
                    self.last_counts[table] = current_count
    
    def monitor_queries(self):
        """Monitor MySQL process list for active queries"""
        print("🔍 Starting MySQL query monitoring...")
        
        while self.monitoring:
            conn = self.get_connection()
            if not conn:
                time.sleep(5)
                continue
                
            try:
                cursor = conn.cursor()
                
                # Get current MySQL process list to see active queries
                cursor.execute("""
                    SELECT id, user, host, db, command, time, state, info 
                    FROM information_schema.processlist 
                    WHERE command != 'Sleep' 
                    AND db = %s 
                    AND info IS NOT NULL
                """, (self.db_config['database'],))
                
                processes = cursor.fetchall()
                
                for process in processes:
                    pid, user, host, db, command, exec_time, state, query = process
                    if query and len(query.strip()) > 0:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"� [{timestamp}] ACTIVE QUERY (PID: {pid})")
                        print(f"   User: {user}@{host}")
                        print(f"   Command: {command} | Time: {exec_time}s | State: {state}")
                        print(f"   Query: {query[:200]}{'...' if len(query) > 200 else ''}")
                        print()
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Error monitoring queries: {e}")
                if conn:
                    conn.close()
            
            time.sleep(3)  # Check every 3 seconds
    
    def print_status(self):
        """Print current status with MySQL-specific information"""
        while self.monitoring:
            time.sleep(30)  # Print status every 30 seconds
            if self.monitoring:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"💡 [{timestamp}] MySQL monitoring active... (Ctrl+C to stop)")
                
                # Get current table counts
                current_counts = self.get_table_counts()
                if current_counts:
                    print("📊 Current table counts:")
                    for table, count in current_counts.items():
                        print(f"   {table}: {count} records")
                
                # Get MySQL server info
                conn = self.get_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT VERSION()")
                        version = cursor.fetchone()[0]
                        
                        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                        connections = cursor.fetchone()[1]
                        
                        cursor.execute("SHOW STATUS LIKE 'Questions'")
                        queries = cursor.fetchone()[1]
                        
                        print(f"🗄️  MySQL Version: {version}")
                        print(f"🔗 Active Connections: {connections}")
                        print(f"📈 Total Queries: {queries}")
                        
                        conn.close()
                    except Exception as e:
                        print(f"❌ Error getting MySQL status: {e}")
                        if conn:
                            conn.close()
                
                print()
    
    def start(self):
        """Start monitoring"""
        print("🚀 Flask Expense Tracker - MySQL Database Monitor")
        print("="*55)
        
        # Test database connection first
        print("🔌 Testing MySQL connection...")
        conn = self.get_connection()
        if not conn:
            print("❌ Failed to connect to MySQL database")
            print("🔧 Please check your database configuration:")
            print(f"   Host: {self.db_config['host']}:{self.db_config['port']}")
            print(f"   Database: {self.db_config['database']}")
            print(f"   User: {self.db_config['user']}")
            return
        
        conn.close()
        print(f"✅ Connected to MySQL database: {self.db_config['database']}")
        
        self.monitoring = True
        
        # Start monitoring threads
        change_thread = Thread(target=self.monitor_changes)
        change_thread.daemon = True
        change_thread.start()
        
        # Disable query monitoring to avoid showing monitoring queries themselves
        # query_thread = Thread(target=self.monitor_queries)
        # query_thread.daemon = True
        # query_thread.start()
        
        status_thread = Thread(target=self.print_status)
        status_thread.daemon = True
        status_thread.start()
        
        try:
            print("🌟 Data change monitoring started! Use your Flask app and see changes here.")
            print("🔗 Visit http://localhost:5003 and add/edit expenses or income")
            print("📊 Only showing actual data changes (INSERT/UPDATE/DELETE)")
            print("⏹️  Press Ctrl+C to stop monitoring\n")
            
            # Keep main thread alive
            while self.monitoring:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
            self.monitoring = False
            print("👋 Monitor stopped!")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Stopping monitor...')
    sys.exit(0)

if __name__ == "__main__":
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # You can customize the database configuration here
    # Or load from environment variables
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'), 
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'adms_expense_dev'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'charset': 'utf8mb4'
    }
    
    print("🔧 MySQL Database Configuration:")
    print(f"   Host: {db_config['host']}:{db_config['port']}")
    print(f"   Database: {db_config['database']}")
    print(f"   User: {db_config['user']}")
    print("   💡 Set environment variables DB_HOST, DB_USER, DB_PASSWORD, DB_NAME if needed")
    print()
    
    # Start monitoring
    monitor = MySQLDatabaseMonitor(db_config)
    monitor.start()