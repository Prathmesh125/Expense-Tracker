#!/bin/bash

# Quick MySQL setup using SQL files
echo "🚀 Quick MySQL Setup using SQL files"
echo "===================================="

# Get credentials
read -p "Enter MySQL username (default: root): " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-root}

read -s -p "Enter MySQL password: " MYSQL_PASSWORD
echo ""

# Create database
echo "📊 Creating database..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS adms_expense CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database created successfully"
else
    echo "❌ Failed to create database"
    exit 1
fi

# Import schema
echo "📋 Importing schema..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" adms_expense < schema.sql 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Schema imported successfully"
else
    echo "❌ Failed to import schema"
    exit 1
fi

# Ask about sample data
read -p "🤔 Import sample data? (y/N): " IMPORT_DATA

if [[ $IMPORT_DATA =~ ^[Yy]$ ]]; then
    echo "📝 Importing sample data..."
    mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" adms_expense < sample_data.sql 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Sample data imported successfully"
        echo ""
        echo "🔐 Sample user credentials:"
        echo "  Username: testuser"
        echo "  Email: test@example.com" 
        echo "  Password: (you'll need to create a user through the app)"
    else
        echo "❌ Failed to import sample data"
    fi
fi

echo ""
echo "✅ Database setup complete!"
echo "🔧 Next steps:"
echo "1. Update your .env file with database credentials"
echo "2. Run: flask run"
