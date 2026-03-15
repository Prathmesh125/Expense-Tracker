# Personal Expense Tracker

A web-based personal expense tracking application built with Python Flask and MySQL, featuring advanced database optimization techniques.

## Features

- **User Authentication**: Secure login and registration system
- **Expense Management**: Add, edit, delete, and categorize expenses
- **Income Tracking**: Record and monitor your income sources
- **Data Visualization**: View spending patterns with charts and graphs
- **Budget Planning**: Set and track budgets for different categories
- **Reports**: Generate financial reports for any time period

## Database Optimization Techniques

This application showcases several advanced database optimization techniques:

1. **Range Partitioning**: Partitions expense data by date ranges for efficient time-based queries
2. **Hash Partitioning**: Evenly distributes user data across partitions to balance system load
3. **Hashing Techniques**: Implements hashing for password security and query optimization

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ADMS_Expense
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the MySQL database:
   - Create a MySQL database
   - Update the `.env` file with your database credentials

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

## Technologies Used

- **Backend**: Python, Flask
- **Database**: MySQL with optimized partitioning
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy
- **Data Visualization**: Matplotlib, Plotly

## Project Structure

```
ADMS_Expense/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models/            # Database models
│   ├── routes/            # Application routes (blueprints)
│   ├── static/            # CSS, JS, images
│   ├── templates/         # HTML templates
│   └── utils/             # Utility functions
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── config.py             # Application configuration
├── MYSQL_MIGRATION.md    # MySQL migration guide
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── run.py                # Application entry point
├── schema.sql            # Database schema with partitioning
├── sample_data.sql       # Sample data for testing
├── setup_mysql.py        # Database setup script
├── manage_partitions.sql # Partition management tools
└── venv/                 # Virtual environment
```
