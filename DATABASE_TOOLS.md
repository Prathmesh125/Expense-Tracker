# Database Tools Summary

## 🛠️ Available Database Tools

Your ADMS Expense Tracker now has a comprehensive suite of database tools:

### 1. **`query_executor.py`** - Advanced Query Tool
**Features:**
- Interactive SQL query execution
- Predefined useful queries
- Tabulated results display
- Export results to JSON
- Support for all SQL commands (SELECT, INSERT, UPDATE, DELETE)
- Auto-configuration from .env file

**Usage:**
```bash
python3 query_executor.py
```

**Best For:** Complex queries, data analysis, one-time operations

---

### 2. **`simple_query.py`** - Lightweight Query Tool
**Features:**
- No external dependencies
- Quick database queries
- Simple table formatting
- Pre-built common queries
- Fast and minimal

**Usage:**
```bash
python3 simple_query.py
```

**Best For:** Quick checks, simple queries, minimal resource usage

---

### 3. **`live_query_monitor.py`** - Professional Database Monitor
**Features:**
- Real-time query monitoring
- Performance statistics (QPS, slow queries, connections)
- Process list monitoring
- Query type breakdown (SELECT, INSERT, UPDATE, DELETE)
- Table statistics with sizes
- Activity logging to JSON files
- Slow query analysis
- Database performance summary

**Usage:**
```bash
python3 live_query_monitor.py
```

**Best For:** Performance monitoring, production debugging, database optimization

---

### 4. **`flask_db_monitor.py`** - Flask App-Specific Monitor
**Features:**
- Flask application-focused monitoring
- User activity tracking
- Real-time database state monitoring
- Monthly/daily activity summaries
- Recent activity feed
- Database size tracking
- Net income/expense calculations per user

**Usage:**
```bash
python3 flask_db_monitor.py
```

**Best For:** Flask app monitoring, user activity analysis, business metrics

---

## 🚀 Quick Start Examples

### Execute a Query
```bash
# Interactive mode
python3 query_executor.py

# Quick query
python3 simple_query.py
```

### Monitor Database Performance
```bash
# Full monitoring suite
python3 live_query_monitor.py

# Flask app specific
python3 flask_db_monitor.py
```

### Common Queries You Can Run

#### User Management
```sql
SELECT * FROM users;
SELECT id, username, email FROM users;
```

#### Financial Data
```sql
SELECT * FROM expenses ORDER BY date DESC LIMIT 10;
SELECT * FROM incomes WHERE date >= '2025-08-01';
SELECT SUM(amount) FROM expenses WHERE MONTH(date) = MONTH(CURDATE());
```

#### Analytics
```sql
SELECT 
    c.name, 
    COUNT(e.id) as expense_count, 
    SUM(e.amount) as total_amount 
FROM categories c 
LEFT JOIN expenses e ON c.id = e.category_id 
GROUP BY c.id, c.name;
```

#### Database Maintenance
```sql
SHOW TABLE STATUS;
ANALYZE TABLE expenses, incomes, categories;
SHOW PROCESSLIST;
```

---

## 🔧 Configuration

All tools automatically read from your `.env` file:
- Uses `DEV_DATABASE_URL` by default
- Falls back to manual configuration if needed
- Supports MySQL connection strings

---

## 📊 Monitoring Capabilities

### Real-time Metrics
- Queries per second (QPS)
- Active connections
- Running threads
- Query type breakdown
- Table row counts and sizes

### Performance Analysis
- Slow query identification
- Connection monitoring
- Database uptime tracking
- Query pattern analysis

### Business Intelligence
- User activity summaries
- Financial data analysis
- Monthly/daily trends
- Recent activity feeds

---

## 🎯 Use Cases

### Development
- Test database queries
- Debug application issues
- Monitor development database activity
- Validate data integrity

### Production Monitoring
- Track performance metrics
- Monitor user activity
- Identify slow queries
- Database health checks

### Data Analysis
- Generate business reports
- Analyze user behavior
- Track financial trends
- Export data for further analysis

---

## 📁 File Sizes
- `query_executor.py`: 14.1 KB (Advanced features)
- `simple_query.py`: 6.3 KB (Lightweight)
- `live_query_monitor.py`: 19.6 KB (Full monitoring)
- `flask_db_monitor.py`: 12.1 KB (App-specific)

**Total**: 52.1 KB of powerful database tools!

---

## 🛡️ Safety Features

- Read-only mode available
- Transaction rollback support
- Connection timeout handling
- Error logging and recovery
- Graceful shutdown (Ctrl+C)

Your database toolkit is now complete and production-ready! 🎉
