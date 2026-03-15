-- MySQL Partitioning Script for ADMS Expense Tracker
-- This script adds partitioning to existing tables
-- WARNING: This will temporarily lock tables and may take time on large datasets

USE adms_expense;

-- Add range partitioning to expenses table
-- This partitions by date for better query performance on time-based queries
ALTER TABLE expenses
PARTITION BY RANGE (YEAR(date) * 100 + MONTH(date)) (
    -- 2024 partitions
    PARTITION p202401 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202407),
    PARTITION p202407 VALUES LESS THAN (202410),
    PARTITION p202410 VALUES LESS THAN (202501),
    
    -- 2025 partitions
    PARTITION p202501 VALUES LESS THAN (202504),
    PARTITION p202504 VALUES LESS THAN (202507),
    PARTITION p202507 VALUES LESS THAN (202510),
    PARTITION p202510 VALUES LESS THAN (202601),
    
    -- 2026 partitions
    PARTITION p202601 VALUES LESS THAN (202604),
    PARTITION p202604 VALUES LESS THAN (202607),
    PARTITION p202607 VALUES LESS THAN (202610),
    PARTITION p202610 VALUES LESS THAN (202701),
    
    -- Future data partition
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- Add range partitioning to incomes table
-- Same partitioning scheme as expenses for consistency
ALTER TABLE incomes
PARTITION BY RANGE (YEAR(date) * 100 + MONTH(date)) (
    -- 2024 partitions
    PARTITION p202401 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202407),
    PARTITION p202407 VALUES LESS THAN (202410),
    PARTITION p202410 VALUES LESS THAN (202501),
    
    -- 2025 partitions
    PARTITION p202501 VALUES LESS THAN (202504),
    PARTITION p202504 VALUES LESS THAN (202507),
    PARTITION p202507 VALUES LESS THAN (202510),
    PARTITION p202510 VALUES LESS THAN (202601),
    
    -- 2026 partitions
    PARTITION p202601 VALUES LESS THAN (202604),
    PARTITION p202604 VALUES LESS THAN (202607),
    PARTITION p202607 VALUES LESS THAN (202610),
    PARTITION p202610 VALUES LESS THAN (202701),
    
    -- Future data partition
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- Add hash partitioning to users table
-- This distributes users evenly across 4 partitions for load balancing
ALTER TABLE users
PARTITION BY HASH(id)
PARTITIONS 4;

-- Verify partitioning was applied
SELECT 
    TABLE_NAME,
    PARTITION_NAME,
    PARTITION_METHOD,
    PARTITION_EXPRESSION,
    PARTITION_DESCRIPTION,
    TABLE_ROWS
FROM INFORMATION_SCHEMA.PARTITIONS 
WHERE TABLE_SCHEMA = 'adms_expense' 
  AND PARTITION_NAME IS NOT NULL
ORDER BY TABLE_NAME, PARTITION_NAME;

-- Show partition information
SHOW CREATE TABLE expenses;
SHOW CREATE TABLE incomes;
SHOW CREATE TABLE users;
