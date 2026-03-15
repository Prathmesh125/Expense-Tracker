#!/bin/bash

# MySQL Database Setup Script for ADMS Expense Tracker
# This script creates the required MySQL databases

echo "MySQL Database Setup for ADMS Expense Tracker"
echo "=============================================="
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed or not in PATH"
    echo "Please install MySQL first:"
    echo "  - macOS: brew install mysql"
    echo "  - Ubuntu/Debian: sudo apt-get install mysql-server"
    echo "  - CentOS/RHEL: sudo yum install mysql-server"
    exit 1
fi

echo "✅ MySQL found"
echo ""

# Get MySQL credentials
read -p "Enter MySQL username (default: root): " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-root}

read -s -p "Enter MySQL password: " MYSQL_PASSWORD
echo ""
echo ""

# Test MySQL connection
echo "🔗 Testing MySQL connection..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1;" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Failed to connect to MySQL. Please check your credentials."
    exit 1
fi

echo "✅ MySQL connection successful"
echo ""

# Create databases
echo "📊 Creating databases..."

mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" << EOF
CREATE DATABASE IF NOT EXISTS adms_expense CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS adms_expense_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS adms_expense_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Show created databases
SHOW DATABASES LIKE 'adms_expense%';
EOF

if [ $? -eq 0 ]; then
    echo "✅ Databases created successfully!"
    echo ""
    echo "📝 Please update your .env file with the following configuration:"
    echo ""
    echo "DATABASE_URL=mysql+pymysql://$MYSQL_USER:YOUR_PASSWORD@localhost/adms_expense"
    echo "DEV_DATABASE_URL=mysql+pymysql://$MYSQL_USER:YOUR_PASSWORD@localhost/adms_expense_dev"
    echo "TEST_DATABASE_URL=mysql+pymysql://$MYSQL_USER:YOUR_PASSWORD@localhost/adms_expense_test"
    echo ""
    echo "Replace YOUR_PASSWORD with your actual MySQL password."
    echo ""
    echo "🚀 Next steps:"
    echo "1. Update the .env file with your MySQL credentials"
    echo "2. Run: flask db init (if migrations folder doesn't exist)"
    echo "3. Run: flask db migrate -m 'Initial migration to MySQL'"
    echo "4. Run: flask db upgrade"
    echo "5. Start your Flask application"
else
    echo "❌ Failed to create databases"
    exit 1
fi
