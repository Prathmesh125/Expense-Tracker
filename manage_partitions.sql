-- Partition Management Script for ADMS Expense Tracker
-- Use this script to manage partitions over time

USE adms_expense;

-- ========================================
-- ADD NEW PARTITIONS (Run this periodically)
-- ========================================

-- Add new partitions for expenses table (example for 2027)
-- ALTER TABLE expenses ADD PARTITION (
--     PARTITION p202701 VALUES LESS THAN (202704),
--     PARTITION p202704 VALUES LESS THAN (202707),
--     PARTITION p202707 VALUES LESS THAN (202710),
--     PARTITION p202710 VALUES LESS THAN (202801)
-- );

-- Add new partitions for incomes table (example for 2027)
-- ALTER TABLE incomes ADD PARTITION (
--     PARTITION p202701 VALUES LESS THAN (202704),
--     PARTITION p202704 VALUES LESS THAN (202707),
--     PARTITION p202707 VALUES LESS THAN (202710),
--     PARTITION p202710 VALUES LESS THAN (202801)
-- );

-- ========================================
-- REMOVE OLD PARTITIONS (Use carefully!)
-- ========================================

-- Example: Remove old 2024 partitions (THIS DELETES DATA!)
-- ALTER TABLE expenses DROP PARTITION p202401, p202404, p202407, p202410;
-- ALTER TABLE incomes DROP PARTITION p202401, p202404, p202407, p202410;

-- ========================================
-- VIEW PARTITION INFORMATION
-- ========================================

-- View all partitions and their row counts
SELECT 
    TABLE_NAME,
    PARTITION_NAME,
    PARTITION_METHOD,
    PARTITION_EXPRESSION,
    PARTITION_DESCRIPTION,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH,
    CREATE_TIME
FROM INFORMATION_SCHEMA.PARTITIONS 
WHERE TABLE_SCHEMA = 'adms_expense' 
  AND PARTITION_NAME IS NOT NULL
ORDER BY TABLE_NAME, PARTITION_ORDINAL_POSITION;

-- View partition sizes
SELECT 
    TABLE_NAME,
    PARTITION_NAME,
    ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'Size (MB)',
    TABLE_ROWS as 'Row Count'
FROM INFORMATION_SCHEMA.PARTITIONS
WHERE TABLE_SCHEMA = 'adms_expense'
  AND PARTITION_NAME IS NOT NULL
ORDER BY TABLE_NAME, PARTITION_NAME;

-- Check which partitions are being used (for recent data)
SELECT 
    p.TABLE_NAME,
    p.PARTITION_NAME,
    p.TABLE_ROWS,
    p.PARTITION_DESCRIPTION
FROM INFORMATION_SCHEMA.PARTITIONS p
WHERE p.TABLE_SCHEMA = 'adms_expense'
  AND p.PARTITION_NAME IS NOT NULL
  AND p.TABLE_ROWS > 0
ORDER BY p.TABLE_NAME, p.PARTITION_ORDINAL_POSITION;

-- ========================================
-- PARTITION PRUNING TEST QUERIES
-- ========================================

-- Test partition pruning for expenses (should only scan relevant partitions)
-- EXPLAIN PARTITIONS 
-- SELECT * FROM expenses 
-- WHERE date >= '2025-08-01' AND date <= '2025-08-31';

-- Test partition pruning for incomes
-- EXPLAIN PARTITIONS 
-- SELECT * FROM incomes 
-- WHERE date >= '2025-08-01' AND date <= '2025-08-31';

-- ========================================
-- PERFORMANCE MONITORING
-- ========================================

-- Check if queries are using partition pruning
-- SELECT 
--     TABLE_NAME,
--     PARTITION_NAME,
--     TABLE_ROWS,
--     AVG_ROW_LENGTH,
--     DATA_LENGTH
-- FROM INFORMATION_SCHEMA.PARTITIONS
-- WHERE TABLE_SCHEMA = 'adms_expense'
--   AND TABLE_NAME IN ('expenses', 'incomes')
--   AND PARTITION_NAME IS NOT NULL;

-- ========================================
-- AUTOMATED PARTITION MAINTENANCE PROCEDURE
-- ========================================

DELIMITER //

CREATE PROCEDURE IF NOT EXISTS AddFuturePartitions()
BEGIN
    DECLARE current_year INT DEFAULT YEAR(CURDATE());
    DECLARE next_year INT DEFAULT current_year + 1;
    DECLARE partition_exists INT DEFAULT 0;
    
    -- Check if next year partitions already exist
    SELECT COUNT(*) INTO partition_exists
    FROM INFORMATION_SCHEMA.PARTITIONS
    WHERE TABLE_SCHEMA = 'adms_expense'
      AND TABLE_NAME = 'expenses'
      AND PARTITION_NAME LIKE CONCAT('p', next_year, '%');
    
    -- Add partitions for next year if they don't exist
    IF partition_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE expenses ADD PARTITION (',
            'PARTITION p', next_year, '01 VALUES LESS THAN (', next_year, '04),',
            'PARTITION p', next_year, '04 VALUES LESS THAN (', next_year, '07),',
            'PARTITION p', next_year, '07 VALUES LESS THAN (', next_year, '10),',
            'PARTITION p', next_year, '10 VALUES LESS THAN (', (next_year + 1), '01)',
            ')');
        
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
        -- Do the same for incomes table
        SET @sql = CONCAT('ALTER TABLE incomes ADD PARTITION (',
            'PARTITION p', next_year, '01 VALUES LESS THAN (', next_year, '04),',
            'PARTITION p', next_year, '04 VALUES LESS THAN (', next_year, '07),',
            'PARTITION p', next_year, '07 VALUES LESS THAN (', next_year, '10),',
            'PARTITION p', next_year, '10 VALUES LESS THAN (', (next_year + 1), '01)',
            ')');
        
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
        SELECT CONCAT('Added partitions for year ', next_year) as Result;
    ELSE
        SELECT 'Partitions already exist for next year' as Result;
    END IF;
END //

DELIMITER ;

-- To run the procedure:
-- CALL AddFuturePartitions();
