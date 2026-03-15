from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Expense, Income, Category, Budget
from app.utils.forms import DateRangeForm, BudgetForm
from app import db
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
from datetime import datetime, timedelta
import calendar
from sqlalchemy import extract, func

reports = Blueprint('reports', __name__)

@reports.route('/reports', methods=['GET', 'POST'])
@login_required
def report_dashboard():
    # Create form for date range selection
    form = DateRangeForm()
    
    # Default to current month if no dates are selected
    today = datetime.today()
    start_of_month = datetime(today.year, today.month, 1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
    else:
        start_date = start_of_month
        end_date = end_of_month
        form.start_date.data = start_date
        form.end_date.data = end_date
    
    # Get all expenses and incomes within the date range
    # Using range partitioning for efficient date-based queries
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).all()
    
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= end_date
    ).all()
    
    # Calculate totals
    total_expense = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)
    balance = total_income - total_expense
    
    # Expense by category chart
    category_data = {}
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        if category_name in category_data:
            category_data[category_name] += expense.amount
        else:
            category_data[category_name] = expense.amount
    
    if category_data:
        # Get labels and values for the chart
        labels = list(category_data.keys())
        values = list(category_data.values())
        
        # Create pie chart using graph_objects for more precise control
        fig_category = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            textinfo='value+percent',
            texttemplate='₹%{value:.2f}<br>(%{percent})',
            hoverinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:.2f}<br>Percentage: %{percent}<extra></extra>',
            marker=dict(
                colors=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', 
                        '#8AC54B', '#F06292', '#26A69A', '#D4E157', '#7986CB', '#FFA726'],
                line=dict(color='white', width=2)
            )
        )])
        
        fig_category.update_layout(
            title=None,
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        
        # Use plotly's built-in JSON serialization which handles NumPy arrays
        category_chart = json.dumps(fig_category.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)
    else:
        category_chart = None
    
    # Daily expense and income chart
    date_range = (end_date - start_date).days + 1
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(date_range)]
    
    # Initialize with zeros
    daily_expenses = {date: 0 for date in dates}
    daily_incomes = {date: 0 for date in dates}
    
    # Fill in actual values
    for expense in expenses:
        date_str = expense.date.strftime('%Y-%m-%d')
        if date_str in daily_expenses:
            daily_expenses[date_str] += expense.amount
    
    for income in incomes:
        date_str = income.date.strftime('%Y-%m-%d')
        if date_str in daily_incomes:
            daily_incomes[date_str] += income.amount
    
    # Create dataframe for time series chart
    df_time = pd.DataFrame({
        'Date': dates,
        'Expense': [daily_expenses[date] for date in dates],
        'Income': [daily_incomes[date] for date in dates]
    })
    
    # Create line chart with improved styling and interactivity
    fig_time = go.Figure()
    
    # Add expense trace with custom styling
    fig_time.add_trace(go.Scatter(
        x=df_time['Date'], 
        y=df_time['Expense'], 
        name='Expense', 
        line=dict(color='#FF6384', width=3),
        mode='lines+markers',
        marker=dict(size=8, line=dict(width=2, color='white')),
        hovertemplate='<b>Date:</b> %{x}<br><b>Expense:</b> ₹%{y:.2f}<extra></extra>'
    ))
    
    # Add income trace with custom styling
    fig_time.add_trace(go.Scatter(
        x=df_time['Date'], 
        y=df_time['Income'], 
        name='Income', 
        line=dict(color='#36A2EB', width=3),
        mode='lines+markers',
        marker=dict(size=8, line=dict(width=2, color='white')),
        hovertemplate='<b>Date:</b> %{x}<br><b>Income:</b> ₹%{y:.2f}<extra></extra>'
    ))
    
    # Improved layout with grid lines and proper formatting
    fig_time.update_layout(
        title=None,
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            tickangle=-45
        ),
        yaxis=dict(
            title='Amount (₹)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.2)'
        ),
        margin=dict(t=10, b=0, l=0, r=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    time_chart = json.dumps(fig_time.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template(
        'reports/dashboard.html',
        title='Reports',
        form=form,
        total_expense=total_expense,
        total_income=total_income,
        balance=balance,
        category_chart=category_chart,
        time_chart=time_chart,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

@reports.route('/reports/monthly')
@login_required
def monthly_report():
    # Get data for the last 12 months - improved calculation
    today = datetime.today()
    # End date is the last day of the previous month
    if today.month == 1:  # January
        end_date = datetime(today.year - 1, 12, 31)
    else:
        end_date = datetime(today.year, today.month - 1, 
                          calendar.monthrange(today.year, today.month - 1)[1])
    
    # Start date is exactly 12 months before the first day of the current month
    if today.month == 1:  # January
        start_date = datetime(today.year - 2, 1, 1)
    else:
        start_date = datetime(today.year - 1, today.month, 1)
    
    # Query the database for monthly totals
    # This is where range partitioning shines for date-based queries
    monthly_expenses = db.session.query(
        extract('year', Expense.date).label('year'),
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= today
    ).group_by(
        extract('year', Expense.date),
        extract('month', Expense.date)
    ).all()
    
    monthly_incomes = db.session.query(
        extract('year', Income.date).label('year'),
        extract('month', Income.date).label('month'),
        func.sum(Income.amount).label('total')
    ).filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= today
    ).group_by(
        extract('year', Income.date),
        extract('month', Income.date)
    ).all()
    
    # Format data for chart - improved month calculation
    months = []
    expense_data = []
    income_data = []
    balance_data = []  # Track monthly balance for trend analysis
    savings_rate = []  # Track savings rate when income > 0
    
    # Get the last 12 months in correct order
    for i in range(12):
        # Calculate month properly with calendar functions
        if today.month - i <= 0:
            year = today.year - 1
            month = 12 + (today.month - i)
        else:
            year = today.year
            month = today.month - i
            
        last_day_of_month = calendar.monthrange(year, month)[1]
        month_date = datetime(year, month, last_day_of_month)
        month_str = month_date.strftime('%b %Y')
        months.insert(0, month_str)
        
        # Find expense for this month
        expense_total = next((e.total for e in monthly_expenses if int(e.year) == year and int(e.month) == month), 0)
        expense_data.insert(0, expense_total)
        
        # Find income for this month
        income_total = next((i.total for i in monthly_incomes if int(i.year) == year and int(i.month) == month), 0)
        income_data.insert(0, income_total)
        
        # Calculate balance and savings rate
        balance = income_total - expense_total
        balance_data.insert(0, balance)
        
        # Calculate savings rate (when income > 0)
        if income_total > 0:
            savings = (income_total - expense_total) / income_total * 100
            savings_rate.insert(0, max(0, savings))  # Only positive savings rate
        else:
            savings_rate.insert(0, 0)
    
    # Create bar chart with improved layout and data visualization
    fig = go.Figure()
    
    # Add income bars with custom styling
    fig.add_trace(go.Bar(
        x=months, 
        y=income_data, 
        name='Income',
        marker_color='#36A2EB',
        marker_line=dict(width=2, color='white'),
        text=['₹' + str(round(val, 2)) for val in income_data],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Income: ₹%{y:.2f}<extra></extra>'
    ))
    
    # Add expense bars with custom styling
    fig.add_trace(go.Bar(
        x=months, 
        y=expense_data, 
        name='Expenses',
        marker_color='#FF6384',
        marker_line=dict(width=2, color='white'),
        text=['₹' + str(round(val, 2)) for val in expense_data],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Expense: ₹%{y:.2f}<extra></extra>'
    ))
    
    # Add balance line to show trend
    fig.add_trace(go.Scatter(
        x=months,
        y=balance_data,
        name='Net Balance',
        line=dict(color='#4BC0C0', width=3, dash='dot'),
        mode='lines+markers',
        marker=dict(size=8, symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Balance: ₹%{y:.2f}<extra></extra>'
    ))
    
    # Improved layout with grid lines and proper formatting
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Month',
            showgrid=False,
            tickangle=-45,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title='Amount (₹)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.2)'
        ),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=30, b=0, l=0, r=0),
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    )
    
    # Prepare data for both chart and template
    monthly_chart = json.dumps(fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)
    
    # Create a dictionary with the chart data for the template with corrected indices
    monthly_data = {
        'months': months,
        'expenses': expense_data,
        'incomes': income_data,
        'balances': balance_data,
        'savings_rates': savings_rate
    }
    
    # Calculate stats for the template
    max_income_index = income_data.index(max(income_data)) if income_data and max(income_data) > 0 else 0
    max_expense_index = expense_data.index(max(expense_data)) if expense_data and max(expense_data) > 0 else 0
    avg_income = sum(income_data) / len(income_data) if income_data else 0
    avg_expense = sum(expense_data) / len(expense_data) if expense_data else 0
    
    # Calculate income and expense trends (positive = increasing, negative = decreasing)
    if len(income_data) >= 2:
        income_trend = (income_data[-1] - income_data[0]) / max(sum(income_data)/len(income_data), 1) * 100
    else:
        income_trend = 0
        
    if len(expense_data) >= 2:
        expense_trend = (expense_data[-1] - expense_data[0]) / max(sum(expense_data)/len(expense_data), 1) * 100
    else:
        expense_trend = 0
        
    # Calculate average savings rate
    avg_savings_rate = sum(savings_rate) / len(savings_rate) if savings_rate else 0
    
    # Identify months with positive vs negative balance
    positive_months = sum(1 for balance in balance_data if balance > 0)
    negative_months = 12 - positive_months
    
    return render_template(
        'reports/monthly.html',
        title='Monthly Report',
        monthly_chart=monthly_chart,
        monthly_data=monthly_data,
        max_income_index=max_income_index,
        max_expense_index=max_expense_index,
        max_income_month=months[max_income_index] if income_data and max(income_data) > 0 else "None",
        max_expense_month=months[max_expense_index] if expense_data and max(expense_data) > 0 else "None",
        max_income_value=income_data[max_income_index] if income_data and max(income_data) > 0 else 0,
        max_expense_value=expense_data[max_expense_index] if expense_data and max(expense_data) > 0 else 0,
        avg_income=avg_income,
        avg_expense=avg_expense,
        income_trend=income_trend,
        expense_trend=expense_trend,
        avg_savings_rate=avg_savings_rate,
        positive_months=positive_months,
        negative_months=negative_months,
        months=months,
        expense_data=expense_data,
        income_data=income_data,
        balance_data=balance_data,
        savings_rate=savings_rate
    )

@reports.route('/reports/budget', methods=['GET', 'POST'])
@login_required
def budget_report():
    # Create form for budget setting
    form = BudgetForm()
    
    # Populate category choices
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        # Check if budget already exists for this category, month and year
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=form.category.data,
            month=form.month.data,
            year=form.year.data
        ).first()
        
        if existing_budget:
            # Update existing budget
            existing_budget.amount = form.amount.data
            flash('Budget updated successfully!', 'success')
        else:
            # Create new budget
            budget = Budget(
                amount=form.amount.data,
                month=form.month.data,
                year=form.year.data,
                category_id=form.category.data,
                user_id=current_user.id
            )
            db.session.add(budget)
            flash('Budget set successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('reports.budget_report'))
    
    # Get current month's budgets
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    
    # Get all budgets for current month and year
    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month,
        year=current_year
    ).all()
    
    # Calculate expenses for each category in current month
    start_of_month = datetime(current_year, current_month, 1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Get all expenses for current month
    expenses_by_category = db.session.query(
        Expense.category_id,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_of_month,
        Expense.date <= end_of_month
    ).group_by(Expense.category_id).all()
    
    # Convert to dictionary for easy lookup
    expense_dict = {e.category_id: e.total for e in expenses_by_category}
    
    # Prepare data for budget vs actual chart
    categories = []
    budget_amounts = []
    actual_amounts = []
    
    for budget in budgets:
        categories.append(budget.category.name if budget.category else 'Uncategorized')
        budget_amounts.append(budget.amount)
        actual_amounts.append(expense_dict.get(budget.category_id, 0))
    
    # Create bar chart
    # Create bar chart
    if categories:
        fig = go.Figure()
        
        # Add budget bars with custom styling
        fig.add_trace(go.Bar(
            x=categories, 
            y=budget_amounts, 
            name='Budget',
            marker_color='#36A2EB',
            marker_line=dict(width=2, color='white'),
            text=['₹' + str(round(val, 2)) for val in budget_amounts],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Budget: ₹%{y:.2f}<extra></extra>'
        ))
        
        # Add actual expense bars with custom styling
        fig.add_trace(go.Bar(
            x=categories, 
            y=actual_amounts, 
            name='Actual',
            marker_color='#FF6384',
            marker_line=dict(width=2, color='white'),
            text=['₹' + str(round(val, 2)) for val in actual_amounts],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Actual: ₹%{y:.2f}<extra></extra>'
        ))
        
        # Calculate and add remaining budget (or overspending) as indicators
        remaining_amounts = [b - a for b, a in zip(budget_amounts, actual_amounts)]
        
        for i, (cat, budget, actual, remaining) in enumerate(zip(categories, budget_amounts, actual_amounts, remaining_amounts)):
            status_color = 'green' if remaining >= 0 else 'red'
            status_text = f'₹{abs(remaining):.2f} {"remaining" if remaining >= 0 else "over budget"}'
            percentage = (actual / budget * 100) if budget > 0 else 0
            
            # Add annotation for each category's status
            fig.add_annotation(
                x=cat,
                y=max(budget, actual) + (max(budget_amounts + actual_amounts) * 0.05),
                text=status_text,
                showarrow=False,
                font=dict(
                    color=status_color,
                    size=10
                )
            )
        
        # Improved layout with grid lines and proper formatting
        fig.update_layout(
            title=None,
            xaxis=dict(
                title=None,
                showgrid=False,
                tickangle=-45,
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                title='Amount (₹)',
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.2)'
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=50, b=0, l=0, r=0),
            plot_bgcolor='rgba(0,0,0,0)',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
        )
        
        budget_chart = json.dumps(fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)
    else:
        budget_chart = None
    
    return render_template(
        'reports/budget.html',
        title='Budget Report',
        form=form,
        budgets=budgets,
        expense_dict=expense_dict,
        budget_chart=budget_chart,
        current_month=calendar.month_name[current_month],
        current_year=current_year
    )
