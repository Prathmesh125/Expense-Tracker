-- Sample Data for ADMS Expense Tracker
-- Insert sample data for testing purposes

USE adms_expense;

-- Insert sample users
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('testuser', 'test@example.com', 'pbkdf2:sha256:260000$test$hash', 'Test', 'User'),
('john_doe', 'john@example.com', 'pbkdf2:sha256:260000$test$hash2', 'John', 'Doe');

-- Insert sample categories for first user
INSERT INTO categories (name, description, user_id) VALUES
('Housing', 'Rent, mortgage, utilities, repairs', 1),
('Transportation', 'Car payments, gas, public transit', 1),
('Food', 'Groceries, dining out, coffee shops', 1),
('Healthcare', 'Insurance, medications, doctor visits', 1),
('Entertainment', 'Movies, concerts, subscriptions', 1),
('Personal', 'Clothing, haircuts, personal care', 1),
('Education', 'Books, courses, school supplies', 1),
('Miscellaneous', 'Other expenses', 1);

-- Insert sample categories for second user
INSERT INTO categories (name, description, user_id) VALUES
('Rent', 'Monthly rent payments', 2),
('Groceries', 'Food and household items', 2),
('Gas', 'Vehicle fuel costs', 2),
('Utilities', 'Electric, water, internet bills', 2);

-- Insert sample expenses for first user
INSERT INTO expenses (amount, description, date, user_id, category_id) VALUES
(1200.00, 'Monthly rent payment', '2025-08-01', 1, 1),
(85.50, 'Grocery shopping at Whole Foods', '2025-08-02', 1, 3),
(45.00, 'Gas station fill-up', '2025-08-03', 1, 2),
(120.00, 'Electric bill', '2025-08-05', 1, 1),
(25.99, 'Netflix subscription', '2025-08-06', 1, 5),
(67.80, 'Dinner at Italian restaurant', '2025-08-07', 1, 3),
(35.00, 'Haircut', '2025-08-08', 1, 6),
(150.00, 'Doctor visit copay', '2025-08-10', 1, 4),
(89.99, 'New running shoes', '2025-08-12', 1, 6),
(42.50, 'Coffee and lunch', '2025-08-14', 1, 3),
(300.00, 'Car insurance payment', '2025-08-15', 1, 2),
(55.75, 'Groceries at local market', '2025-08-16', 1, 3),
(12.99, 'Book purchase', '2025-08-18', 1, 7),
(95.00, 'Internet bill', '2025-08-19', 1, 1),
(28.50, 'Movie tickets', '2025-08-20', 1, 5);

-- Insert sample expenses for second user
INSERT INTO expenses (amount, description, date, user_id, category_id) VALUES
(800.00, 'Rent payment', '2025-08-01', 2, 9),
(65.30, 'Weekly groceries', '2025-08-03', 2, 10),
(40.00, 'Gas fill-up', '2025-08-05', 2, 11),
(78.50, 'Electric and water bill', '2025-08-07', 2, 12),
(52.75, 'Grocery shopping', '2025-08-10', 2, 10),
(35.00, 'Gas station', '2025-08-12', 2, 11),
(90.00, 'Internet bill', '2025-08-15', 2, 12);

-- Insert sample incomes for first user
INSERT INTO incomes (amount, source, description, date, user_id) VALUES
(3500.00, 'Salary', 'Monthly salary payment', '2025-08-01', 1),
(500.00, 'Freelance', 'Web design project', '2025-08-08', 1),
(150.00, 'Investment', 'Dividend payment', '2025-08-15', 1),
(75.00, 'Side Hustle', 'Online tutoring', '2025-08-18', 1);

-- Insert sample incomes for second user
INSERT INTO incomes (amount, source, description, date, user_id) VALUES
(2800.00, 'Salary', 'Monthly salary', '2025-08-01', 2),
(200.00, 'Part-time', 'Weekend job', '2025-08-10', 2),
(100.00, 'Bonus', 'Performance bonus', '2025-08-15', 2);

-- Insert sample budgets for first user
INSERT INTO budgets (amount, month, year, user_id, category_id) VALUES
(1300.00, 8, 2025, 1, 1),  -- Housing budget
(400.00, 8, 2025, 1, 2),   -- Transportation budget
(500.00, 8, 2025, 1, 3),   -- Food budget
(200.00, 8, 2025, 1, 4),   -- Healthcare budget
(150.00, 8, 2025, 1, 5),   -- Entertainment budget
(200.00, 8, 2025, 1, 6);   -- Personal budget

-- Insert sample budgets for second user
INSERT INTO budgets (amount, month, year, user_id, category_id) VALUES
(850.00, 8, 2025, 2, 9),   -- Rent budget
(300.00, 8, 2025, 2, 10),  -- Groceries budget
(200.00, 8, 2025, 2, 11),  -- Gas budget
(150.00, 8, 2025, 2, 12);  -- Utilities budget

-- Verify data insertion
SELECT 'Users' as Table_Name, COUNT(*) as Record_Count FROM users
UNION ALL
SELECT 'Categories', COUNT(*) FROM categories
UNION ALL
SELECT 'Expenses', COUNT(*) FROM expenses
UNION ALL
SELECT 'Incomes', COUNT(*) FROM incomes
UNION ALL
SELECT 'Budgets', COUNT(*) FROM budgets;
