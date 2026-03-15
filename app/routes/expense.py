from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Expense, Category
from app.utils.forms import ExpenseForm
from app.utils.hash_utils import generate_transaction_hash
from datetime import datetime, timedelta

expense = Blueprint('expense', __name__)

@expense.route('/expenses')
@login_required
def expenses():
    # Get page number and filters from query parameters
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date_filter', 'all')
    category_id = request.args.get('category_id', '')
    search_query = request.args.get('search', '')
    
    # Debug log filter parameters
    print(f"Filter params: date_filter={date_filter}, start_date={request.args.get('start_date')}, end_date={request.args.get('end_date')}, category={category_id}, search={search_query}")
    
    # Build the base query
    query = Expense.query.filter_by(user_id=current_user.id)
    
    # Apply date filter
    today = datetime.today().date()  # Use date objects consistently since the model uses Date type
    from_date = None
    to_date = None
    
    if date_filter == 'this_month':
        # First day of current month
        from_date = datetime(today.year, today.month, 1).date()
        # Last day of current month
        if today.month == 12:
            to_date = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            to_date = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
            
    elif date_filter == 'last_month':
        # Calculate last month (handling January case)
        last_month = today.month - 1 if today.month > 1 else 12
        last_month_year = today.year if today.month > 1 else today.year - 1
        
        # First day of last month
        from_date = datetime(last_month_year, last_month, 1).date()
        # Last day of last month
        to_date = datetime(today.year, today.month, 1).date() - timedelta(days=1)
        
    elif date_filter == 'this_year':
        from_date = datetime(today.year, 1, 1).date()
        to_date = datetime(today.year, 12, 31).date()
        
    elif date_filter == 'last_year':
        from_date = datetime(today.year - 1, 1, 1).date()
        to_date = datetime(today.year - 1, 12, 31).date()
        
    elif date_filter == 'custom':
        # Parse custom date range
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            try:
                # Convert string dates to date objects (not datetime)
                from_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                # Log the date conversion for debugging
                print(f"Custom date range: from {from_date} to {to_date}")
            except ValueError as e:
                # If date parsing fails, log the error and don't apply the filter
                print(f"Date parsing error: {e}")
                pass
    
    # Debug info for date filters
    print(f"Date filter: {date_filter}, from_date: {from_date}, to_date: {to_date}")
                
    # Apply date filters to query - compare date with date
    if from_date:
        query = query.filter(Expense.date >= from_date)
    if to_date:
        query = query.filter(Expense.date <= to_date)
        
    # Apply category filter
    if category_id and category_id.isdigit():
        query = query.filter(Expense.category_id == int(category_id))
        
    # Apply search query
    if search_query:
        query = query.filter(Expense.description.like(f'%{search_query}%') | 
                           Expense.notes.like(f'%{search_query}%'))
    
    # Get all expenses with pagination (15 per page)
    # Range partitioning on date makes this query efficient
    expenses_list = query.order_by(Expense.date.desc()).paginate(page=page, per_page=15)
    
    # Calculate statistics based on filter selection
    today = datetime.today()
    
    # Set period title based on date filter
    period_title = "All Time"
    if date_filter == 'this_month':
        dt = datetime(today.year, today.month, 1)
        period_title = f"{dt.strftime('%B %Y')}"
    elif date_filter == 'last_month':
        # Calculate last month (handling January case)
        last_month = today.month - 1 if today.month > 1 else 12
        last_month_year = today.year if today.month > 1 else today.year - 1
        
        dt = datetime(last_month_year, last_month, 1)
        period_title = f"{dt.strftime('%B %Y')}"
    elif date_filter == 'this_year':
        period_title = f"{today.year}"
    elif date_filter == 'last_year':
        period_title = f"{today.year - 1}"
    elif date_filter == 'custom':
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                period_title = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
            except ValueError:
                period_title = "Custom Range"
    
    # Calculate statistics based on the filtered data
    # Use aggregate functions for performance instead of fetching all records
    
    # Total for the filtered period
    filtered_total = query.with_entities(db.func.sum(Expense.amount)).scalar() or 0
    
    # Calculate daily average if there's a date range
    daily_avg = 0
    
    if date_filter != 'all' and from_date and to_date:
        # Use the date range from the filter directly
        days_in_range = (to_date - from_date).days + 1
        if days_in_range > 0:
            daily_avg = filtered_total / days_in_range
    elif date_filter != 'all':
        # If there's a filter but we don't have explicit dates, calculate based on data
        min_date_result = query.with_entities(db.func.min(Expense.date)).first()
        max_date_result = query.with_entities(db.func.max(Expense.date)).first()
        
        if min_date_result[0] and max_date_result[0]:
            min_date = min_date_result[0]
            max_date = max_date_result[0]
            days_in_range = (max_date - min_date).days + 1
            if days_in_range > 0:
                daily_avg = filtered_total / days_in_range
    
    # Get highest expense in filtered data
    highest_expense_result = query.with_entities(db.func.max(Expense.amount)).first()
    highest_expense = highest_expense_result[0] if highest_expense_result and highest_expense_result[0] else 0
    
    # Count categories used in filtered data
    if category_id and category_id.isdigit():
        # If filtering by a specific category, there's just one category
        categories_used = 1
    else:
        # Count distinct categories using an efficient database query
        distinct_categories = query.with_entities(Expense.category_id).distinct().filter(Expense.category_id.isnot(None)).count()
        categories_used = distinct_categories
    
    # Get all categories for filter dropdown
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    
    return render_template(
        'expense/expenses.html', 
        title='Expenses', 
        expenses=expenses_list,
        period_title=period_title,
        filtered_total=filtered_total,
        daily_avg=daily_avg,
        highest_expense=highest_expense,
        total_categories=categories_used,
        categories=categories
    )

@expense.route('/expense/new', methods=['GET', 'POST'])
@login_required
def new_expense():
    form = ExpenseForm()
    
    # Populate category choices
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    # Add "Uncategorized" option
    form.category.choices.insert(0, (0, 'Uncategorized'))
    
    if form.validate_on_submit():
        # Generate hash for duplicate detection
        transaction_hash = generate_transaction_hash(
            current_user.id, 
            form.amount.data, 
            form.date.data, 
            form.description.data
        )
        
        # Check for duplicates (optional, can be enabled for strict duplicate prevention)
        #existing_expense = Expense.query.filter_by(transaction_hash=transaction_hash).first()
        #if existing_expense:
        #    flash('This expense appears to be a duplicate. Please verify.', 'warning')
        #    return redirect(url_for('expense.expenses'))
        
        # Create expense
        expense = Expense(
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
            user_id=current_user.id,
            category_id=form.category.data if form.category.data > 0 else None
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense has been added!', 'success')
        return redirect(url_for('expense.expenses'))
    
    return render_template('expense/create_expense.html', title='New Expense', form=form, legend='New Expense')

@expense.route('/expense/<int:expense_id>')
@login_required
def expense_detail(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Ensure the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You do not have permission to view this expense.', 'danger')
        return redirect(url_for('expense.expenses'))
    
    # Get similar expenses (same category, excluding current expense)
    similar_expenses = []
    if expense.category_id:
        similar_expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.category_id == expense.category_id,
            Expense.id != expense.id
        ).order_by(Expense.date.desc()).limit(5).all()
    
    return render_template(
        'expense/expense_detail.html', 
        title='Expense Detail', 
        expense=expense,
        similar_expenses=similar_expenses
    )

@expense.route('/expense/<int:expense_id>/update', methods=['GET', 'POST'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Ensure the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You do not have permission to update this expense.', 'danger')
        return redirect(url_for('expense.expenses'))
    
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    form.category.choices.insert(0, (0, 'Uncategorized'))
    
    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.description = form.description.data
        expense.date = form.date.data
        expense.category_id = form.category.data if form.category.data > 0 else None
        
        db.session.commit()
        flash('Your expense has been updated!', 'success')
        return redirect(url_for('expense.expense_detail', expense_id=expense.id))
    
    elif request.method == 'GET':
        form.amount.data = expense.amount
        form.description.data = expense.description
        form.date.data = expense.date
        form.category.data = expense.category_id if expense.category_id else 0
    
    return render_template('expense/create_expense.html', title='Update Expense', form=form, legend='Update Expense')

@expense.route('/expense/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Ensure the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You do not have permission to delete this expense.', 'danger')
        return redirect(url_for('expense.expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Your expense has been deleted!', 'success')
    return redirect(url_for('expense.expenses'))

@expense.route('/categories')
@login_required
def categories():
    categories_list = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('expense/categories.html', title='Categories', categories=categories_list)

@expense.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = ExpenseForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category has been added!', 'success')
        return redirect(url_for('expense.categories'))
    
    return render_template('expense/create_category.html', title='New Category', form=form, legend='New Category')
