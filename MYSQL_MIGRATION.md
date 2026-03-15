# MySQL Migration Guide

This guide explains how to migrate from SQLite to MySQL for the ADMS Expense Tracker.

## Prerequisites

1. **MySQL Server**: Ensure MySQL is installed and running
   ```bash
   # macOS (using Homebrew)
   brew install mysql
   brew services start mysql
   
   # Ubuntu/Debian
   sudo apt-get install mysql-server
   sudo systemctl start mysql
   
   # CentOS/RHEL
   sudo yum install mysql-server
   sudo systemctl start mysqld
   ```

2. **Python Packages**: The required packages are already in requirements.txt
   - `mysql-connector-python`
   - `pymysql`

## Migration Steps

### 1. Database Setup

Choose one of the following methods:

#### Option A: Using the Python setup script
```bash
python setup_mysql.py
```

#### Option B: Using the shell script
```bash
./setup_mysql.sh
```

#### Option C: Manual setup
```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create databases
CREATE DATABASE adms_expense CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE adms_expense_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE adms_expense_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Update Environment Variables

Update your `.env` file with MySQL connection strings:

```properties
DATABASE_URL=mysql+pymysql://username:password@localhost/adms_expense
DEV_DATABASE_URL=mysql+pymysql://username:password@localhost/adms_expense_dev
TEST_DATABASE_URL=mysql+pymysql://username:password@localhost/adms_expense_test
```

Replace `username` and `password` with your actual MySQL credentials.

### 3. Initialize Flask-Migrate

If you don't have a migrations folder:

```bash
source venv/bin/activate
flask db init
```

### 4. Create Migration

Generate the initial migration for MySQL:

```bash
flask db migrate -m "Initial migration to MySQL"
```

### 5. Apply Migration

Apply the migration to create tables:

```bash
flask db upgrade
```

### 6. Start the Application

```bash
flask run
```

## Changes Made

### Configuration Changes
- Updated `config.py` to use MySQL connection strings instead of SQLite
- Updated `.env` file with MySQL database URLs

### Database Partitioning
- Enhanced `app/utils/db_partitioning.py` to support MySQL partitioning
- Added fallback to indexes if partitioning fails
- Maintains SQLite compatibility for development

### Files Removed
- All `.db` files (SQLite databases)

### New Features
- MySQL partitioning for improved performance
- Better database connection handling
- Setup scripts for easy migration

## Database Schema

The application uses the following tables:
- `users` - User accounts with hash partitioning
- `expenses` - Expense records with date range partitioning  
- `incomes` - Income records with date range partitioning
- `categories` - Expense categories
- `budgets` - Budget planning

## Performance Optimizations

### MySQL Partitioning
- **Expenses table**: Range partitioned by date (quarterly partitions)
- **Incomes table**: Range partitioned by date (quarterly partitions)  
- **Users table**: Hash partitioned for load balancing

### Indexes
- Automatic indexes on foreign keys
- Date indexes for time-based queries
- User ID indexes for data filtering

## Troubleshooting

### Common Issues

1. **Connection Error**: Check MySQL service is running
   ```bash
   # macOS
   brew services restart mysql
   
   # Linux
   sudo systemctl restart mysql
   ```

2. **Permission Denied**: Ensure user has database creation privileges
   ```sql
   GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Character Set Issues**: Ensure databases use UTF-8
   ```sql
   ALTER DATABASE adms_expense CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. **Migration Errors**: Drop and recreate migrations if needed
   ```bash
   rm -rf migrations/
   flask db init
   flask db migrate -m "Fresh MySQL migration"
   flask db upgrade
   ```

## Rollback to SQLite

If you need to rollback to SQLite:

1. Update `.env` file to comment out MySQL URLs
2. Update `config.py` to use SQLite paths
3. Create fresh migrations
4. Run the application

## Performance Benefits

MySQL provides several advantages over SQLite:

- **Concurrent Access**: Better handling of multiple users
- **Partitioning**: Improved query performance on large datasets
- **Scalability**: Better performance with large amounts of data
- **Advanced Features**: Views, stored procedures, triggers
- **Production Ready**: Suitable for production deployments
