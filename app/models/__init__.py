from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model with hash partitioning (implicit through user_id which will be hash partitioned)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    monthly_budget = db.Column(db.Float, default=0.0)  # Overall monthly budget
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy='dynamic')
    incomes = db.relationship('Income', backref='user', lazy='dynamic')
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_email_hash(self):
        """Create a hash of the email for efficient lookup"""
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
    
    def __repr__(self):
        return f'<User {self.username}>'

# Category model
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    monthly_budget = db.Column(db.Float, default=0.0)  # Monthly budget limit for this category
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')
    
    def get_current_month_spending(self):
        """Calculate total spending for current month in this category"""
        from datetime import datetime
        today = datetime.today()
        first_day = datetime(today.year, today.month, 1).date()
        if today.month == 12:
            last_day = datetime(today.year + 1, 1, 1).date()
        else:
            last_day = datetime(today.year, today.month + 1, 1).date()
        
        total = db.session.query(db.func.sum(Expense.amount)).\
            filter(Expense.category_id == self.id).\
            filter(Expense.date >= first_day).\
            filter(Expense.date < last_day).scalar()
        
        return total or 0.0
    
    def is_over_budget(self):
        """Check if category spending is over budget for current month"""
        if self.monthly_budget <= 0:
            return False
        return self.get_current_month_spending() > self.monthly_budget
    
    def budget_usage_percentage(self):
        """Get percentage of budget used"""
        if self.monthly_budget <= 0:
            return 0
        return (self.get_current_month_spending() / self.monthly_budget) * 100
    
    def __repr__(self):
        return f'<Category {self.name}>'

# Expense model with range partitioning (implicit through date field)
class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(256))
    date = db.Column(db.Date, nullable=False, index=True)  # Range partitioning key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Generate hash for duplicate detection (optional use)
    def generate_hash(self):
        """Generate a hash of the expense for duplicate detection"""
        content = f"{self.user_id}-{self.amount}-{self.date}-{self.description}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def __repr__(self):
        return f'<Expense {self.amount} on {self.date}>'

# Income model with range partitioning (implicit through date field)
class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(128))
    description = db.Column(db.String(256))
    date = db.Column(db.Date, nullable=False, index=True)  # Range partitioning key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Income {self.amount} on {self.date}>'

# Budget model
class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Relationships
    category = db.relationship('Category', backref='budgets')
    
    def __repr__(self):
        return f'<Budget {self.amount} for {self.month}/{self.year}>'
