from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=256)])
    date = DateField('Date', validators=[DataRequired()], default=datetime.utcnow)
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Add Expense')

class IncomeForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    source = StringField('Source', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[Length(max=256)])
    date = DateField('Date', validators=[DataRequired()], default=datetime.utcnow)
    submit = SubmitField('Add Income')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Length(max=256)])
    submit = SubmitField('Add Category')

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
