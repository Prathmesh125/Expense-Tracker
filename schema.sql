-- MySQL Database Schema for ADMS Expense Tracker
-- Created: August 2025
-- Database: adms_expense

USE adms_expense;

-- Drop tables if they exist (for clean setup)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS incomes;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS alembic_version;
SET FOREIGN_KEY_CHECKS = 1;

-- Users table with hash partitioning capability
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Categories table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    description VARCHAR(256),
    user_id INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_categories_user_id (user_id),
    INDEX idx_categories_name (name)
);

-- Expenses table with range partitioning by date
CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(256),
    date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    category_id INT,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_expenses_date (date),
    INDEX idx_expenses_user_id (user_id),
    INDEX idx_expenses_category_id (category_id)
);

-- Incomes table with range partitioning by date
CREATE TABLE incomes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    source VARCHAR(128),
    description VARCHAR(256),
    date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_incomes_date (date),
    INDEX idx_incomes_user_id (user_id)
);

-- Budgets table
CREATE TABLE budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    user_id INT NOT NULL,
    category_id INT,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_budgets_user_id (user_id),
    INDEX idx_budgets_date (year, month)
);

-- Alembic version table for Flask-Migrate
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Set up range partitioning for expenses table by date
-- This improves query performance for date-based filtering
ALTER TABLE expenses
PARTITION BY RANGE (YEAR(date) * 100 + MONTH(date)) (
    PARTITION p202401 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202407),
    PARTITION p202407 VALUES LESS THAN (202410),
    PARTITION p202410 VALUES LESS THAN (202501),
    PARTITION p202501 VALUES LESS THAN (202504),
    PARTITION p202504 VALUES LESS THAN (202507),
    PARTITION p202507 VALUES LESS THAN (202510),
    PARTITION p202510 VALUES LESS THAN (202601),
    PARTITION p202601 VALUES LESS THAN (202604),
    PARTITION p202604 VALUES LESS THAN (202607),
    PARTITION p202607 VALUES LESS THAN (202610),
    PARTITION p202610 VALUES LESS THAN (202701),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- Set up range partitioning for incomes table by date
-- This improves query performance for date-based filtering
ALTER TABLE incomes
PARTITION BY RANGE (YEAR(date) * 100 + MONTH(date)) (
    PARTITION p202401 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202407),
    PARTITION p202407 VALUES LESS THAN (202410),
    PARTITION p202410 VALUES LESS THAN (202501),
    PARTITION p202501 VALUES LESS THAN (202504),
    PARTITION p202504 VALUES LESS THAN (202507),
    PARTITION p202507 VALUES LESS THAN (202510),
    PARTITION p202510 VALUES LESS THAN (202601),
    PARTITION p202601 VALUES LESS THAN (202604),
    PARTITION p202604 VALUES LESS THAN (202607),
    PARTITION p202607 VALUES LESS THAN (202610),
    PARTITION p202610 VALUES LESS THAN (202701),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- Set up hash partitioning for users table
-- This distributes users evenly across partitions for load balancing
ALTER TABLE users
PARTITION BY HASH(id)
PARTITIONS 4;
