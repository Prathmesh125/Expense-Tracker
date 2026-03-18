from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User
from app.utils.forms import RegistrationForm, LoginForm, ProfileSettingsForm, ChangePasswordForm
from app.utils.hash_utils import generate_password_hash, verify_password_hash
from app.utils.default_data import create_default_categories

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.password_hash = generate_password_hash(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default categories for the new user
        create_default_categories(user.id)
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and verify_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    settings_form = ProfileSettingsForm(original_email=current_user.email)
    password_form = ChangePasswordForm()
    
    # Handle profile settings update
    if settings_form.validate_on_submit() and 'profile_submit' in request.form:
        current_user.first_name = settings_form.first_name.data
        current_user.last_name = settings_form.last_name.data
        current_user.email = settings_form.email.data
        current_user.monthly_budget = settings_form.monthly_budget.data or 0.0
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Handle password change
    if password_form.validate_on_submit() and 'password_submit' in request.form:
        if verify_password_hash(current_user.password_hash, password_form.current_password.data):
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    # Populate form with current user data
    if request.method == 'GET':
        settings_form.first_name.data = current_user.first_name
        settings_form.last_name.data = current_user.last_name
        settings_form.email.data = current_user.email
        settings_form.monthly_budget.data = current_user.monthly_budget
    
    return render_template('auth/profile.html', title='Profile', 
                         settings_form=settings_form, 
                         password_form=password_form)
