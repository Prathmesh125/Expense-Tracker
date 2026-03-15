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

## Security Features

This application includes comprehensive security measures:

- **Input Validation**: Comprehensive validation for all user inputs
- **Input Sanitization**: XSS and injection attack prevention
- **Rate Limiting**: Protection against brute force and DoS attacks
- **Security Headers**: CSP, X-Frame-Options, and other security headers
- **Error Handling**: Graceful error handling with custom error pages
- **Password Hashing**: Secure password storage using Werkzeug
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM

## Deployment Guide

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8 or higher
- MySQL 8.0 or higher
- Nginx (for production)
- Supervisor (for process management)

### Production Deployment Steps

#### 1. Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv mysql-server nginx supervisor -y
```

#### 2. Database Configuration

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE adms_expense;
CREATE USER 'adms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON adms_expense.* TO 'adms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Application Setup

```bash
# Clone repository
cd /var/www
sudo git clone <repository-url> adms_expense
cd adms_expense

# Create virtual environment
sudo python3 -m venv venv
sudo chown -R $USER:$USER venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 4. Environment Configuration

Create and configure `.env` file:

```bash
sudo nano .env
```

Add the following configuration:

```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-change-this
DATABASE_URL=mysql+pymysql://adms_user:your_secure_password@localhost/adms_expense
DB_HOST=localhost
DB_PORT=3306
DB_USER=adms_user
DB_PASSWORD=your_secure_password
DB_NAME=adms_expense
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

#### 5. Database Migration

```bash
# Initialize database
flask db upgrade

# Add default categories
flask add-default-categories
```

#### 6. Gunicorn Configuration

Create `gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/var/www/adms_expense/logs/gunicorn_error.log"
accesslog = "/var/www/adms_expense/logs/gunicorn_access.log"
loglevel = "info"
```

#### 7. Supervisor Configuration

Create `/etc/supervisor/conf.d/adms_expense.conf`:

```ini
[program:adms_expense]
directory=/var/www/adms_expense
command=/var/www/adms_expense/venv/bin/gunicorn --config gunicorn_config.py run:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/adms_expense/err.log
stdout_logfile=/var/log/adms_expense/out.log
```

Update and start supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start adms_expense
```

#### 8. Nginx Configuration

Create `/etc/nginx/sites-available/adms_expense`:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/adms_expense/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/adms_expense /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your_domain.com
```

#### 10. Database Backup

Set up automated backups using cron:

```bash
# Create backup directory
sudo mkdir -p /var/backups/adms_expense
sudo chown $USER:$USER /var/backups/adms_expense

# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /var/www/adms_expense && /var/www/adms_expense/venv/bin/python backup_database.py --action backup --keep 7
```

### Monitoring and Maintenance

#### Health Check

Monitor application health:

```bash
curl http://your_domain.com/health
```

#### View Logs

```bash
# Application logs
tail -f /var/www/adms_expense/logs/adms_expense.log

# Gunicorn logs
tail -f /var/www/adms_expense/logs/gunicorn_error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### Restart Application

```bash
sudo supervisorctl restart adms_expense
```

### Performance Optimization

1. **Enable MySQL query caching**
2. **Configure connection pooling** (already configured in `config.py`)
3. **Use CDN for static assets**
4. **Enable Nginx gzip compression**
5. **Set up Redis for session management** (optional)

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Check MySQL credentials in `.env`
2. **Permission Denied**: Ensure correct file permissions (`chown -R www-data:www-data /var/www/adms_expense`)
3. **Port Already in Use**: Change port in `gunicorn_config.py`
4. **Module Not Found**: Activate virtual environment and install dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainer.
