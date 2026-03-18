from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(message='Please enter a username.'), 
                                    Length(min=2, max=20, message='Username must be between 2 and 20 characters.')])
    email = StringField('Email', 
                       validators=[DataRequired(message='Please enter your email address.'), 
                                 Email(message='Please enter a valid email address.')])
    password = PasswordField('Password', 
                           validators=[DataRequired(message='Please enter a password.')])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(message='Please confirm your password.'), 
                                              EqualTo('password', message='Passwords must match.')])
    first_name = StringField('First Name', 
                            validators=[DataRequired(message='Please enter your first name.'), 
                                      Length(max=64, message='First name cannot exceed 64 characters.')])
    last_name = StringField('Last Name', 
                           validators=[DataRequired(message='Please enter your last name.'), 
                                     Length(max=64, message='Last name cannot exceed 64 characters.')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with this email already exists. Please log in or use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(message='Please enter your email address.'), 
                                 Email(message='Please enter a valid email address.')])
    password = PasswordField('Password', 
                           validators=[DataRequired(message='Please enter your password.')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', 
                       validators=[DataRequired(message='Please enter an amount.')])
    description = TextAreaField('Description', 
                               validators=[Length(max=256, message='Description cannot exceed 256 characters.')])
    notes = TextAreaField('Notes', 
                         validators=[Length(max=1000, message='Notes cannot exceed 1000 characters.')])
    date = DateField('Date', 
                    validators=[DataRequired(message='Please select a date.')], 
                    default=datetime.utcnow)
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Add Expense')

class IncomeForm(FlaskForm):
    amount = FloatField('Amount', 
                       validators=[DataRequired(message='Please enter an amount.')])
    source = StringField('Source', 
                        validators=[DataRequired(message='Please enter the income source.'), 
                                  Length(max=128, message='Source cannot exceed 128 characters.')])
    description = TextAreaField('Description', 
                               validators=[Length(max=256, message='Description cannot exceed 256 characters.')])
    date = DateField('Date', 
                    validators=[DataRequired(message='Please select a date.')], 
                    default=datetime.utcnow)
    submit = SubmitField('Add Income')

class CategoryForm(FlaskForm):
    name = StringField('Name', 
                      validators=[DataRequired(message='Please enter a category name.'), 
                                Length(max=64, message='Category name cannot exceed 64 characters.')])
    description = TextAreaField('Description', 
                               validators=[Length(max=256, message='Description cannot exceed 256 characters.')])
    color = StringField('Color', 
                       validators=[Length(max=7, message='Color must be a valid hex code.')],
                       default='#6c757d')
    icon = SelectField('Icon', 
                      choices=[
                          ('fa-shopping-cart', 'Shopping Cart'),
                          ('fa-utensils', 'Food & Dining'),
                          ('fa-car', 'Transportation'),
                          ('fa-home', 'Housing'),
                          ('fa-heartbeat', 'Healthcare'),
                          ('fa-film', 'Entertainment'),
                          ('fa-graduation-cap', 'Education'),
                          ('fa-plane', 'Travel'),
                          ('fa-tshirt', 'Clothing'),
                          ('fa-tag', 'General')
                      ])
    monthly_budget = FloatField('Monthly Budget (₹)')
    submit = SubmitField('Save Category')

class BudgetForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    month = SelectField('Month', choices=[(1, 'January'), (2, 'February'), (3, 'March'), 
                                          (4, 'April'), (5, 'May'), (6, 'June'), 
                                          (7, 'July'), (8, 'August'), (9, 'September'), 
                                          (10, 'October'), (11, 'November'), (12, 'December')], coerce=int)
    year = SelectField('Year', coerce=int)
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Set Budget')
    
    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        # Populate years (current year + 5 years ahead)
        current_year = datetime.utcnow().year
        self.year.choices = [(y, str(y)) for y in range(current_year, current_year + 6)]

class DateRangeForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], default=datetime.utcnow)
    end_date = DateField('End Date', validators=[DataRequired()], default=datetime.utcnow)
    submit = SubmitField('Generate Report')

class ProfileSettingsForm(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[DataRequired(message='Please enter your first name.'), 
                                      Length(max=64, message='First name cannot exceed 64 characters.')])
    last_name = StringField('Last Name', 
                           validators=[DataRequired(message='Please enter your last name.'), 
                                     Length(max=64, message='Last name cannot exceed 64 characters.')])
    email = StringField('Email', 
                       validators=[DataRequired(message='Please enter your email address.'), 
                                 Email(message='Please enter a valid email address.')])
    monthly_budget = FloatField('Monthly Budget (₹)', 
                               validators=[])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileSettingsForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already registered to another account.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', 
                                    validators=[DataRequired(message='Please enter your current password.')])
    new_password = PasswordField('New Password', 
                                validators=[DataRequired(message='Please enter a new password.'), 
                                          Length(min=8, message='Password must be at least 8 characters long.')])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[DataRequired(message='Please confirm your new password.'), 
                                              EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')
