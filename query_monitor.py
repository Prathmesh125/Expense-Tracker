#!/usr/bin/env python3
"""
Real-time Query and Interface Action Monitor for ADMS Expense Tracker
This tool monitors database queries and user interface actions in real-time.
"""

import os
import time
import threading
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from flask import Flask, request, g
import json
import sqlite3
import socket
import atexit
from collections import deque, defaultdict
from termcolor import colored
import sys
import argparse
import logging
from contextlib import contextmanager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a queue to store recent queries and actions
MAX_HISTORY_SIZE = 1000
query_history = deque(maxlen=MAX_HISTORY_SIZE)
action_history = deque(maxlen=MAX_HISTORY_SIZE)

# Statistics counters
stats = {
    'total_queries': 0,
    'select_queries': 0,
    'insert_queries': 0,
    'update_queries': 0,
    'delete_queries': 0,
    'other_queries': 0,
    'slow_queries': 0,
    'interface_actions': defaultdict(int),
    'route_hits': defaultdict(int),
    'query_times': []
}

class QueryMonitor:
    def __init__(self, db_config=None, use_sqlite=False):
        self.connection = None
        self.monitoring = False
        self.db_config = db_config
        self.use_sqlite = use_sqlite
        self.sqlite_path = None
        self.proxy_socket = None
        self.proxy_port = 3307  # Default proxy port
        self.monitoring_thread = None
        
    def load_config(self):
        """Load database configuration from .env file if not provided"""
        if self.db_config:
            return
            
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if 'DEV_DATABASE_URL=' in line:
                        url = line.split('=', 1)[1].strip()
                        if 'mysql+pymysql://' in url:
                            url = url.replace('mysql+pymysql://', '')
                            auth, host_db = url.split('@')
                            user, password = auth.split(':', 1) if ':' in auth else (auth, '')
                            host, database = host_db.split('/', 1) if '/' in host_db else (host_db, '')
                            
                            self.db_config = {
                                'host': host, 'user': user, 
                                'password': password, 'database': database
                            }
                            break
        except Exception as e:
            logger.error(f"Failed to load config from .env: {e}")
            
    def connect_mysql(self):
        """Connect to MySQL database"""
        if not self.db_config:
            self.load_config()
            
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info(f"✅ Connected to MySQL: {self.db_config['database']}")
            return True
        except Error as e:
            logger.error(f"❌ MySQL connection failed: {e}")
            return False
            
    def connect_sqlite(self):
        """Create SQLite database for storing query log"""
        try:
            self.sqlite_path = 'query_monitor.db'
            conn = sqlite3.connect(self.sqlite_path)
            c = conn.cursor()
            
            # Create tables if they don't exist
            c.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                query TEXT,
                duration REAL,
                rows_affected INTEGER,
                query_type TEXT
            )
            ''')
            
            c.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_id INTEGER,
                route TEXT,
                method TEXT,
                status_code INTEGER,
                duration REAL,
                data TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ SQLite database created at {self.sqlite_path}")
            return True
        except Exception as e:
            logger.error(f"❌ SQLite setup failed: {e}")
            return False
            
    def setup_proxy(self):
        """Set up a proxy server to intercept MySQL queries"""
        # This is a simple implementation - a production version would 
        # need more sophisticated MySQL protocol handling
        try:
            self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.proxy_socket.bind(('localhost', self.proxy_port))
            self.proxy_socket.listen(5)
            
            logger.info(f"✅ Proxy listening on port {self.proxy_port}")
            
            # Register cleanup function
            atexit.register(self.cleanup)
            
            return True
        except Exception as e:
            logger.error(f"❌ Proxy setup failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.proxy_socket:
            self.proxy_socket.close()
        
        if self.connection:
            self.connection.close()
            
        logger.info("🧹 Resources cleaned up")
    
    def log_query(self, query, duration, rows_affected=0, query_type='UNKNOWN'):
        """Log a query to the history and SQLite if enabled"""
        timestamp = datetime.now()
        
        # Determine query type if not provided
        if query_type == 'UNKNOWN':
            query_lower = query.lower().strip()
            if query_lower.startswith('select'):
                query_type = 'SELECT'
                stats['select_queries'] += 1
            elif query_lower.startswith('insert'):
                query_type = 'INSERT'
                stats['insert_queries'] += 1
            elif query_lower.startswith('update'):
                query_type = 'UPDATE'
                stats['update_queries'] += 1
            elif query_lower.startswith('delete'):
                query_type = 'DELETE'
                stats['delete_queries'] += 1
            else:
                query_type = 'OTHER'
                stats['other_queries'] += 1
        
        # Update statistics
        stats['total_queries'] += 1
        stats['query_times'].append(duration)
        
        if duration > 1.0:  # Queries taking more than 1 second
            stats['slow_queries'] += 1
            
        # Add to memory queue
        query_entry = {
            'timestamp': timestamp,
            'query': query,
            'duration': duration,
            'rows_affected': rows_affected,
            'query_type': query_type
        }
        query_history.append(query_entry)
        
        # Log to SQLite if enabled
        if self.use_sqlite and self.sqlite_path:
            try:
                conn = sqlite3.connect(self.sqlite_path)
                c = conn.cursor()
                c.execute('''
                INSERT INTO queries (timestamp, query, duration, rows_affected, query_type)
                VALUES (?, ?, ?, ?, ?)
                ''', (timestamp.isoformat(), query, duration, rows_affected, query_type))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to log query to SQLite: {e}")
    
    def log_action(self, user_id, route, method, status_code, duration, data=None):
        """Log a user interface action"""
        timestamp = datetime.now()
        
        # Update statistics
        stats['interface_actions'][method] += 1
        stats['route_hits'][route] += 1
        
        # Convert data to JSON string if it's a dict
        data_str = json.dumps(data) if isinstance(data, dict) else str(data) if data else None
        
        # Add to memory queue
        action_entry = {
            'timestamp': timestamp,
            'user_id': user_id,
            'route': route,
            'method': method,
            'status_code': status_code,
            'duration': duration,
            'data': data_str
        }
        action_history.append(action_entry)
        
        # Log to SQLite if enabled
        if self.use_sqlite and self.sqlite_path:
            try:
                conn = sqlite3.connect(self.sqlite_path)
                c = conn.cursor()
                c.execute('''
                INSERT INTO actions (timestamp, user_id, route, method, status_code, duration, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp.isoformat(), user_id, route, method, status_code, duration, data_str))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to log action to SQLite: {e}")
    
    def monitor_mysql_general_log(self):
        """Monitor the MySQL general log for queries"""
        if not self.connection:
            logger.error("❌ Not connected to MySQL")
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Enable general log if needed
            cursor.execute("SET GLOBAL log_output = 'TABLE'")
            cursor.execute("SET GLOBAL general_log = 1")
            
            logger.info("✅ MySQL general log enabled")
            
            # Get the last log ID
            cursor.execute("SELECT MAX(event_time) FROM mysql.general_log")
            last_timestamp = cursor.fetchone()[0] or datetime.now()
            
            while self.monitoring:
                try:
                    cursor.execute("""
                    SELECT event_time, user_host, argument 
                    FROM mysql.general_log 
                    WHERE event_time > %s
                    ORDER BY event_time
                    """, (last_timestamp,))
                    
                    rows = cursor.fetchall()
                    if rows:
                        for row in rows:
                            event_time, user_host, query = row
                            last_timestamp = event_time
                            
                            # Skip system queries
                            if "general_log" in query or query.startswith("SELECT @@"):
                                continue
                                
                            # Log the query with estimated duration (not available from general_log)
                            self.log_query(query, 0.0)
                    
                    time.sleep(0.5)  # Poll every 0.5 seconds
                except Exception as e:
                    logger.error(f"Error polling general log: {e}")
                    time.sleep(5)  # Back off on error
                    
        except Exception as e:
            logger.error(f"Failed to monitor MySQL general log: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def display_live_monitor(self):
        """Display a live monitor of queries and actions"""
        try:
            while self.monitoring:
                os.system('clear' if os.name == 'posix' else 'cls')
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(colored(f"🔍 ADMS Expense Tracker - Real-time Monitor ({current_time})", "cyan", attrs=['bold']))
                print(colored("=" * 80, "cyan"))
                
                # Display statistics
                print(colored("📊 Statistics:", "yellow", attrs=['bold']))
                print(f"  Queries: {stats['total_queries']} total, {stats['select_queries']} SELECT, "
                      f"{stats['insert_queries']} INSERT, {stats['update_queries']} UPDATE, "
                      f"{stats['delete_queries']} DELETE, {stats['slow_queries']} slow")
                
                # Calculate average query time
                avg_time = sum(stats['query_times'][-100:]) / len(stats['query_times'][-100:]) if stats['query_times'] else 0
                print(f"  Average query time (last 100): {avg_time:.4f}s")
                
                # Display top routes
                print(colored("\n🛣️  Top Routes:", "yellow", attrs=['bold']))
                top_routes = sorted(stats['route_hits'].items(), key=lambda x: x[1], reverse=True)[:5]
                for route, count in top_routes:
                    print(f"  {route}: {count} hits")
                
                # Display recent queries
                print(colored("\n🔍 Recent Queries:", "green", attrs=['bold']))
                for entry in list(query_history)[-5:]:
                    query_type = entry['query_type']
                    color = "blue" if query_type == "SELECT" else "magenta" if query_type == "INSERT" else "yellow"
                    timestamp = entry['timestamp'].strftime("%H:%M:%S")
                    duration = entry['duration']
                    
                    # Truncate long queries for display
                    query = entry['query']
                    if len(query) > 70:
                        query = query[:67] + "..."
                        
                    print(colored(f"  [{timestamp}] ", "white") + 
                          colored(f"[{query_type}] ", color) + 
                          f"{query} ({duration:.4f}s)")
                
                # Display recent actions
                print(colored("\n👤 Recent Interface Actions:", "green", attrs=['bold']))
                for entry in list(action_history)[-5:]:
                    method = entry['method']
                    color = "green" if method == "GET" else "yellow" if method == "POST" else "red"
                    timestamp = entry['timestamp'].strftime("%H:%M:%S")
                    status = entry['status_code']
                    status_color = "green" if status < 400 else "red"
                    
                    print(colored(f"  [{timestamp}] ", "white") + 
                          colored(f"[{method}] ", color) + 
                          f"{entry['route']} - " +
                          colored(f"Status: {status}", status_color) +
                          f" ({entry['duration']:.4f}s)")
                
                print(colored("\n⏱️  Press Ctrl+C to stop monitoring...", "white"))
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(colored("\n🛑 Monitoring stopped", "red"))
    
    def start(self, display_mode=True):
        """Start monitoring"""
        self.monitoring = True
        
        # Setup database connections
        if self.use_sqlite:
            if not self.connect_sqlite():
                return False
                
        if not self.connect_mysql():
            return False
            
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_mysql_general_log)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        if display_mode:
            self.display_live_monitor()
        
        return True
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
            
        self.cleanup()


class FlaskQueryMonitor:
    """Flask middleware to monitor queries and actions"""
    
    def __init__(self, app=None, query_monitor=None):
        self.query_monitor = query_monitor
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        # Before request
        @app.before_request
        def before_request():
            g.start_time = time.time()
        
        # After request
        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                user_id = g.user.id if hasattr(g, 'user') and hasattr(g.user, 'id') else None
                
                # Collect form data if it's a form submission
                data = None
                if request.form:
                    data = {k: v for k, v in request.form.items() if k not in ['password', 'csrf_token']}
                
                # Log the action
                if self.query_monitor:
                    self.query_monitor.log_action(
                        user_id=user_id,
                        route=request.path,
                        method=request.method,
                        status_code=response.status_code,
                        duration=duration,
                        data=data
                    )
            
            return response


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Real-time Query and Interface Action Monitor')
    parser.add_argument('--no-display', action='store_true', help='Run without display (background mode)')
    parser.add_argument('--sqlite', action='store_true', help='Enable SQLite logging')
    parser.add_argument('--proxy-port', type=int, default=3307, help='Proxy server port (default: 3307)')
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    print(colored("🚀 ADMS Expense Tracker - Real-time Query & Action Monitor", "cyan", attrs=['bold']))
    print(colored("=" * 80, "cyan"))
    
    # Initialize monitor
    monitor = QueryMonitor(use_sqlite=args.sqlite)
    monitor.proxy_port = args.proxy_port
    
    # Start monitoring
    try:
        if monitor.start(display_mode=not args.no_display):
            if args.no_display:
                print(colored("✅ Monitor running in background mode", "green"))
                # Keep the main thread alive
                while monitor.monitoring:
                    time.sleep(1)
    except KeyboardInterrupt:
        print(colored("\n👋 Shutting down...", "yellow"))
    finally:
        monitor.stop()


def configure_flask_app(app, use_sqlite=False):
    """Configure Flask app with query monitoring"""
    monitor = QueryMonitor(use_sqlite=use_sqlite)
    flask_monitor = FlaskQueryMonitor(app, monitor)
    
    # Start monitoring thread
    if monitor.connect_mysql() and (not use_sqlite or monitor.connect_sqlite()):
        threading.Thread(target=monitor.monitor_mysql_general_log, daemon=True).start()
        logger.info("✅ Flask query monitoring enabled")
    
    return monitor, flask_monitor


if __name__ == "__main__":
    main()
