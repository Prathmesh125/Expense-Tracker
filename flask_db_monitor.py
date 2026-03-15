#!/usr/bin/env python3
"""
Flask App Database Activity Monitor
Monitors database queries specific to ADMS Expense Tracker Flask application
"""

import os
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import threading
from collections import defaultdict

class FlaskAppMonitor:
    def __init__(self):
        self.connection = None
        self.monitoring = False
        self.config = {}
        self.query_stats = defaultdict(int)
        self.last_stats = {}
        
    def connect(self):
        """Connect using .env configuration"""
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
                            
                            self.config = {
                                'host': host, 'user': user, 
                                'password': password, 'database': database
                            }
                            break
            
            self.connection = mysql.connector.connect(**self.config)
            print(f"✅ Connected to {self.config['database']}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_flask_relevant_stats(self):
        """Get statistics relevant to Flask app"""
        cursor = self.connection.cursor()
        
        stats = {}
        
        try:
            # Table row counts
            tables = ['users', 'expenses', 'incomes', 'categories', 'budgets']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
            
            # Recent activity (last 24 hours)
            cursor.execute("SELECT COUNT(*) FROM expenses WHERE created_at >= NOW() - INTERVAL 1 DAY")
            stats['expenses_today'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM incomes WHERE created_at >= NOW() - INTERVAL 1 DAY")
            stats['incomes_today'] = cursor.fetchone()[0]
            
            # Monthly totals
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(amount) as total 
                FROM expenses 
                WHERE YEAR(date) = YEAR(CURDATE()) AND MONTH(date) = MONTH(CURDATE())
            """)
            result = cursor.fetchone()
            stats['monthly_expense_count'] = result[0]
            stats['monthly_expense_total'] = result[1] or 0
            
            cursor.execute("""
                SELECT COUNT(*) as count, SUM(amount) as total 
                FROM incomes 
                WHERE YEAR(date) = YEAR(CURDATE()) AND MONTH(date) = MONTH(CURDATE())
            """)
            result = cursor.fetchone()
            stats['monthly_income_count'] = result[0]
            stats['monthly_income_total'] = result[1] or 0
            
            # Database size
            cursor.execute("""
                SELECT 
                    ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as size_mb
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s
            """, (self.config['database'],))
            stats['database_size_mb'] = cursor.fetchone()[0] or 0
            
        except Error as e:
            print(f"❌ Stats error: {e}")
        finally:
            cursor.close()
            
        return stats
    
    def monitor_flask_activity(self):
        """Monitor Flask app database activity"""
        print("🔍 Monitoring Flask App Database Activity")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        self.monitoring = True
        
        try:
            while self.monitoring:
                os.system('clear' if os.name == 'posix' else 'cls')
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🐍 Flask App Database Monitor - {current_time}")
                print("=" * 50)
                
                stats = self.get_flask_relevant_stats()
                
                if stats:
                    print("📊 Current Database State:")
                    print(f"   Users: {stats.get('users_count', 0):,}")
                    print(f"   Categories: {stats.get('categories_count', 0):,}")
                    print(f"   Expenses: {stats.get('expenses_count', 0):,}")
                    print(f"   Incomes: {stats.get('incomes_count', 0):,}")
                    print(f"   Budgets: {stats.get('budgets_count', 0):,}")
                    
                    print(f"\n📈 Today's Activity:")
                    print(f"   New Expenses: {stats.get('expenses_today', 0)}")
                    print(f"   New Incomes: {stats.get('incomes_today', 0)}")
                    
                    print(f"\n📅 This Month:")
                    print(f"   Expense Count: {stats.get('monthly_expense_count', 0):,}")
                    print(f"   Expense Total: ${stats.get('monthly_expense_total', 0):,.2f}")
                    print(f"   Income Count: {stats.get('monthly_income_count', 0):,}")
                    print(f"   Income Total: ${stats.get('monthly_income_total', 0):,.2f}")
                    
                    print(f"\n💾 Database Size: {stats.get('database_size_mb', 0):.2f} MB")
                    
                    # Show changes from last check
                    if self.last_stats:
                        changes = []
                        for key, value in stats.items():
                            if key in self.last_stats:
                                diff = value - self.last_stats[key]
                                if diff != 0 and 'count' in key:
                                    changes.append(f"{key}: +{diff}")
                        
                        if changes:
                            print(f"\n🔄 Changes since last check:")
                            for change in changes:
                                print(f"   {change}")
                    
                    self.last_stats = stats.copy()
                
                print(f"\n⏱️  Refreshing every 5 seconds...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
        finally:
            self.monitoring = False
    
    def show_user_activity(self):
        """Show user-specific activity"""
        cursor = self.connection.cursor()
        
        try:
            print("👥 User Activity Summary:")
            print("-" * 40)
            
            cursor.execute("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    COUNT(DISTINCT e.id) as expense_count,
                    COUNT(DISTINCT i.id) as income_count,
                    COUNT(DISTINCT c.id) as category_count,
                    COALESCE(SUM(e.amount), 0) as total_expenses,
                    COALESCE(SUM(i.amount), 0) as total_incomes
                FROM users u
                LEFT JOIN expenses e ON u.id = e.user_id
                LEFT JOIN incomes i ON u.id = i.user_id  
                LEFT JOIN categories c ON u.id = c.user_id
                GROUP BY u.id, u.username, u.email
                ORDER BY expense_count DESC
            """)
            
            users = cursor.fetchall()
            
            for user in users:
                print(f"\n🧑 User: {user[1]} ({user[2]})")
                print(f"   Expenses: {user[3]:,} records (${user[6]:,.2f})")
                print(f"   Incomes: {user[4]:,} records (${user[7]:,.2f})")
                print(f"   Categories: {user[5]:,}")
                
                net = user[7] - user[6]  # income - expenses
                print(f"   Net: ${net:,.2f}")
        
        except Error as e:
            print(f"❌ User activity error: {e}")
        finally:
            cursor.close()
    
    def show_recent_activity(self):
        """Show recent database changes"""
        cursor = self.connection.cursor()
        
        try:
            print("🕐 Recent Activity (Last 24 Hours):")
            print("-" * 40)
            
            # Recent expenses
            cursor.execute("""
                SELECT 
                    'EXPENSE' as type,
                    e.created_at,
                    e.amount,
                    e.description,
                    u.username,
                    c.name as category
                FROM expenses e
                LEFT JOIN users u ON e.user_id = u.id
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.created_at >= NOW() - INTERVAL 1 DAY
                
                UNION ALL
                
                SELECT 
                    'INCOME' as type,
                    i.created_at,
                    i.amount,
                    i.source as description,
                    u.username,
                    NULL as category
                FROM incomes i
                LEFT JOIN users u ON i.user_id = u.id
                WHERE i.created_at >= NOW() - INTERVAL 1 DAY
                
                ORDER BY created_at DESC
                LIMIT 20
            """)
            
            activities = cursor.fetchall()
            
            if not activities:
                print("   No recent activity")
            else:
                for activity in activities:
                    type_icon = "💸" if activity[0] == "EXPENSE" else "💰"
                    time_str = activity[1].strftime("%H:%M:%S")
                    print(f"   {type_icon} {time_str} | ${activity[2]:6.2f} | {activity[4]} | {activity[3][:30]}")
        
        except Error as e:
            print(f"❌ Recent activity error: {e}")
        finally:
            cursor.close()
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
        print("🔌 Connection closed")

def main():
    print("🐍 Flask App Database Activity Monitor")
    print("=" * 40)
    
    monitor = FlaskAppMonitor()
    
    if not monitor.connect():
        return
    
    try:
        while True:
            print("\n🎯 Monitor Options:")
            print("1. Live activity monitoring")
            print("2. User activity summary")
            print("3. Recent activity (24h)")
            print("4. Database overview")
            print("0. Exit")
            
            choice = input("\nSelect (0-4): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                monitor.monitor_flask_activity()
            elif choice == "2":
                monitor.show_user_activity()
                input("\nPress Enter to continue...")
            elif choice == "3":
                monitor.show_recent_activity()
                input("\nPress Enter to continue...")
            elif choice == "4":
                stats = monitor.get_flask_relevant_stats()
                print(f"\n📊 Database Overview:")
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        print(f"   {key}: {value:,}")
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        monitor.close()

if __name__ == "__main__":
    main()
