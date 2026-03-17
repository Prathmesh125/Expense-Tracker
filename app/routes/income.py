from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response
from flask_login import login_required, current_user
from app import db
from app.models import Income
from app.utils.forms import IncomeForm
from datetime import datetime, timedelta
import csv
import io

income = Blueprint('income', __name__)

@income.route('/incomes')
@login_required
def incomes():
    # Get page number, filters, search, and sorting from query parameters
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date_filter', 'all')
    source_filter = request.args.get('source', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Start with the base query
    query = Income.query.filter_by(user_id=current_user.id)
    
    # Apply date filters
    today = datetime.today()
    from_date = None
    to_date = None
    period_title = "All Time"
    
    if date_filter == 'this_month':
        from_date = datetime(today.year, today.month, 1)
        # Next month, day 1, minus 1 day
        to_date = datetime(today.year + (today.month // 12), 
                          ((today.month % 12) + 1), 1)
        to_date = to_date.replace(day=1) - timedelta(days=1)
        period_title = f"{today.strftime('%B %Y')}"
    elif date_filter == 'last_month':
        # Last month
        last_month = today.month - 1 if today.month > 1 else 12
        last_month_year = today.year if today.month > 1 else today.year - 1
        from_date = datetime(last_month_year, last_month, 1)
        to_date = datetime(today.year, today.month, 1) - timedelta(days=1)
        period_title = f"{from_date.strftime('%B %Y')}"
    elif date_filter == 'this_year':
        from_date = datetime(today.year, 1, 1)
        to_date = datetime(today.year, 12, 31)
        period_title = f"{today.year}"
    elif date_filter == 'last_year':
        from_date = datetime(today.year - 1, 1, 1)
        to_date = datetime(today.year - 1, 12, 31)
        period_title = f"{today.year - 1}"
    elif date_filter == 'custom':
        try:
            from_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else None
            to_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') if request.args.get('end_date') else None
            if from_date and to_date:
                period_title = f"{from_date.strftime('%b %d, %Y')} - {to_date.strftime('%b %d, %Y')}"
            elif from_date:
                period_title = f"Since {from_date.strftime('%b %d, %Y')}"
            elif to_date:
                period_title = f"Until {to_date.strftime('%b %d, %Y')}"
        except ValueError:
            # Handle invalid date format
            pass
    
    # Apply filters to the query
    if from_date:
        query = query.filter(Income.date >= from_date)
    if to_date:
        query = query.filter(Income.date <= to_date)
    if source_filter:
        query = query.filter(Income.source == source_filter)
    
    # Apply search query
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (Income.source.like(search_pattern)) | 
            (Income.description.like(search_pattern))
        )
    
    # Get all sources for the filter dropdown (only for current user)
    all_sources = db.session.query(Income.source).filter(Income.user_id == current_user.id).distinct().all()
    sources = [source[0] for source in all_sources if source[0]]
    
    # Get statistics for the current filter
    total_income = query.with_entities(db.func.sum(Income.amount)).scalar() or 0
    count = query.count()
    avg_income = total_income / count if count > 0 else 0
    
    # Get monthly total
    current_month_query = Income.query.filter_by(user_id=current_user.id)
    current_month_query = current_month_query.filter(
        Income.date >= datetime(today.year, today.month, 1),
        Income.date <= datetime(today.year + (today.month // 12), 
                              ((today.month % 12) + 1), 1) - timedelta(days=1)
    )
    monthly_total = current_month_query.with_entities(db.func.sum(Income.amount)).scalar() or 0
    
    # Apply sorting
    if sort_by == 'amount':
        if sort_order == 'asc':
            query = query.order_by(Income.amount.asc())
        else:
            query = query.order_by(Income.amount.desc())
    elif sort_by == 'source':
        if sort_order == 'asc':
            query = query.order_by(Income.source.asc(), Income.date.desc())
        else:
            query = query.order_by(Income.source.desc(), Income.date.desc())
    else:  # Default to date sorting
        if sort_order == 'asc':
            query = query.order_by(Income.date.asc())
        else:
            query = query.order_by(Income.date.desc())
    
    # Sort and paginate
    incomes_list = query.paginate(page=page, per_page=10)
    
    # Calculate if filters are active
    is_filtered = date_filter != 'all' or source_filter != '' or search_query != ''
    
    return render_template(
        'income/incomes.html', 
        title='Incomes', 
        incomes=incomes_list,
        sources=sources,
        total_income=total_income,
        avg_income=avg_income,
        monthly_total=monthly_total,
        period_title=period_title,
        is_filtered=is_filtered,
        today=today
    )

@income.route('/income/new', methods=['GET', 'POST'])
@login_required
def new_income():
    form = IncomeForm()
    
    if form.validate_on_submit():
        income = Income(
            amount=form.amount.data,
            source=form.source.data,
            description=form.description.data,
            date=form.date.data,
            user_id=current_user.id
        )
        
        db.session.add(income)
        db.session.commit()
        
        flash('Income has been added!', 'success')
        return redirect(url_for('income.incomes'))
    
    return render_template('income/create_income.html', title='New Income', form=form, legend='New Income')

@income.route('/income/<int:income_id>')
@login_required
def income_detail(income_id):
    income = Income.query.get_or_404(income_id)
    
    # Ensure the income belongs to the current user
    if income.user_id != current_user.id:
        flash('You do not have permission to view this income.', 'danger')
        return redirect(url_for('income.incomes'))
    
    return render_template('income/income_detail.html', title='Income Detail', income=income)

@income.route('/income/<int:income_id>/update', methods=['GET', 'POST'])
@login_required
def update_income(income_id):
    income = Income.query.get_or_404(income_id)
    
    # Ensure the income belongs to the current user
    if income.user_id != current_user.id:
        flash('You do not have permission to update this income.', 'danger')
        return redirect(url_for('income.incomes'))
    
    form = IncomeForm()
    
    if form.validate_on_submit():
        income.amount = form.amount.data
        income.source = form.source.data
        income.description = form.description.data
        income.date = form.date.data
        
        db.session.commit()
        flash('Your income has been updated!', 'success')
        return redirect(url_for('income.income_detail', income_id=income.id))
    
    elif request.method == 'GET':
        form.amount.data = income.amount
        form.source.data = income.source
        form.description.data = income.description
        form.date.data = income.date
    
    return render_template('income/create_income.html', title='Update Income', form=form, legend='Update Income')

@income.route('/income/<int:income_id>/delete', methods=['POST'])
@login_required
def delete_income(income_id):
    income = Income.query.get_or_404(income_id)
    
    # Ensure the income belongs to the current user
    if income.user_id != current_user.id:
        flash('You do not have permission to delete this income.', 'danger')
        return redirect(url_for('income.incomes'))
    
    db.session.delete(income)
    db.session.commit()
    flash('Your income has been deleted!', 'success')
    return redirect(url_for('income.incomes'))

@income.route('/incomes/export')
@login_required
def export_incomes():
    """Export incomes to CSV file"""
    # Get filter parameters (same as incomes route)
    date_filter = request.args.get('date_filter', 'all')
    source_filter = request.args.get('source', '')
    search_query = request.args.get('search', '')
    
    # Start with the base query
    query = Income.query.filter_by(user_id=current_user.id)
    
    # Apply date filters
    today = datetime.today()
    from_date = None
    to_date = None
    
    if date_filter == 'this_month':
        from_date = datetime(today.year, today.month, 1)
        to_date = datetime(today.year + (today.month // 12), 
                          ((today.month % 12) + 1), 1)
        to_date = to_date.replace(day=1) - timedelta(days=1)
    elif date_filter == 'last_month':
        last_month = today.month - 1 if today.month > 1 else 12
        last_month_year = today.year if today.month > 1 else today.year - 1
        from_date = datetime(last_month_year, last_month, 1)
        to_date = datetime(today.year, today.month, 1) - timedelta(days=1)
    elif date_filter == 'this_year':
        from_date = datetime(today.year, 1, 1)
        to_date = datetime(today.year, 12, 31)
    elif date_filter == 'last_year':
        from_date = datetime(today.year - 1, 1, 1)
        to_date = datetime(today.year - 1, 12, 31)
    elif date_filter == 'custom':
        try:
            from_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d') if request.args.get('start_date') else None
            to_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') if request.args.get('end_date') else None
        except ValueError:
            pass
    
    # Apply filters to the query
    if from_date:
        query = query.filter(Income.date >= from_date)
    if to_date:
        query = query.filter(Income.date <= to_date)
    if source_filter:
        query = query.filter(Income.source == source_filter)
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (Income.source.like(search_pattern)) | 
            (Income.description.like(search_pattern))
        )
    
    # Get all incomes (no pagination for export)
    incomes_list = query.order_by(Income.date.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Source', 'Description', 'Amount'])
    
    # Write data rows
    for inc in incomes_list:
        writer.writerow([
            inc.date.strftime('%Y-%m-%d'),
            inc.source or '',
            inc.description or '',
            f'{inc.amount:.2f}'
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=incomes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response
