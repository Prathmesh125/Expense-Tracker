from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Expense, Income, Category
from app import db
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='Welcome')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get current month expenses and incomes
    today = datetime.today()
    start_of_month = datetime(today.year, today.month, 1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Get last month dates for comparison
    if today.month == 1:
        last_month_start = datetime(today.year - 1, 12, 1)
        last_month_end = datetime(today.year, 1, 1) - timedelta(days=1)
    else:
        last_month_start = datetime(today.year, today.month - 1, 1)
        last_month_end = start_of_month - timedelta(days=1)
    
    # Fetch data from the database using the range partitioning advantage
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_of_month,
        Expense.date <= end_of_month
    ).all()
    
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= start_of_month,
        Income.date <= end_of_month
    ).all()
    
    # Fetch last month data for comparison
    last_month_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= last_month_start,
        Expense.date <= last_month_end
    ).all()
    
    last_month_incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= last_month_start,
        Income.date <= last_month_end
    ).all()
    
    # Calculate totals
    total_expense = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)
    balance = total_income - total_expense
    
    # Calculate last month totals
    last_month_expense = sum(expense.amount for expense in last_month_expenses)
    last_month_income = sum(income.amount for income in last_month_incomes)
    
    # Calculate percentage changes
    expense_change = ((total_expense - last_month_expense) / last_month_expense * 100) if last_month_expense > 0 else 0
    income_change = ((total_income - last_month_income) / last_month_income * 100) if last_month_income > 0 else 0
    
    # Calculate daily average
    days_in_month = (end_of_month - start_of_month).days + 1
    daily_avg_expense = total_expense / days_in_month if days_in_month > 0 else 0
    
    # Get expense by category data for pie chart and top categories
    categories = {}
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        if category_name in categories:
            categories[category_name] += expense.amount
        else:
            categories[category_name] = expense.amount
    
    # Create pie chart for expenses by category
    if categories:
        # Get labels and values for the chart
        labels = list(categories.keys())
        values = list(categories.values())
        
        # Create pie chart using graph_objects for more precise control
        fig_category = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            textinfo='value+percent',
            texttemplate='₹%{value:.2f}<br>(%{percent})',
            hoverinfo='label+value+percent',
            hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:.2f}<br>Percentage: %{percent}<extra></extra>',
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
    
    # Create bar chart for income vs expense
    income_expense_df = pd.DataFrame({
        'Type': ['Income', 'Expense'],
        'Amount': [total_income, total_expense]
    })
    
    # Create bar chart using graph_objects for more precise control
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=['Income', 'Expense'],
        y=[total_income, total_expense],
        text=['₹' + str(round(total_income, 2)), '₹' + str(round(total_expense, 2))],
        textposition='outside',
        marker=dict(
            color=['#36A2EB', '#FF6384'],
            line=dict(color='white', width=2)
        )
    ))
    
    fig2.update_layout(
        title=None,
        xaxis=dict(title=None),
        yaxis=dict(title='Amount (₹)', gridcolor='rgba(0,0,0,0.1)'),
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Use plotly's built-in JSON serialization which handles NumPy arrays
    income_expense_chart = json.dumps(fig2.to_dict(), cls=plotly.utils.PlotlyJSONEncoder)
    
    # Get last 5 transactions
    last_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    last_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    
    # Check budget alerts
    budget_alerts = []
    
    # Check overall monthly budget
    if current_user.monthly_budget > 0:
        budget_usage_pct = (total_expense / current_user.monthly_budget) * 100
        if budget_usage_pct >= 100:
            budget_alerts.append({
                'type': 'danger',
                'category': 'Overall Budget',
                'message': f'You have exceeded your monthly budget by ₹{total_expense - current_user.monthly_budget:.2f}!',
                'percentage': budget_usage_pct
            })
        elif budget_usage_pct >= 90:
            budget_alerts.append({
                'type': 'warning',
                'category': 'Overall Budget',
                'message': f'You have used {budget_usage_pct:.0f}% of your monthly budget.',
                'percentage': budget_usage_pct
            })
        elif budget_usage_pct >= 75:
            budget_alerts.append({
                'type': 'info',
                'category': 'Overall Budget',
                'message': f'You have used {budget_usage_pct:.0f}% of your monthly budget.',
                'percentage': budget_usage_pct
            })
    
    # Check category budgets
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    for cat in user_categories:
        if cat.monthly_budget > 0:
            cat_spending = cat.get_current_month_spending()
            cat_usage_pct = (cat_spending / cat.monthly_budget) * 100
            
            if cat_usage_pct >= 100:
                budget_alerts.append({
                    'type': 'danger',
                    'category': cat.name,
                    'message': f'{cat.name} is over budget by ₹{cat_spending - cat.monthly_budget:.2f}!',
                    'percentage': cat_usage_pct
                })
            elif cat_usage_pct >= 90:
                budget_alerts.append({
                    'type': 'warning',
                    'category': cat.name,
                    'message': f'{cat.name} has used {cat_usage_pct:.0f}% of budget.',
                    'percentage': cat_usage_pct
                })
    
    # Get top 5 spending categories
    top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template(
        'main/dashboard.html',
        title='Dashboard',
        today=today,
        total_expense=total_expense,
        total_income=total_income,
        balance=balance,
        category_chart=category_chart,
        income_expense_chart=income_expense_chart,
        last_expenses=last_expenses,
        last_incomes=last_incomes,
        budget_alerts=budget_alerts,
        # New analytics data
        expense_change=expense_change,
        income_change=income_change,
        last_month_expense=last_month_expense,
        last_month_income=last_month_income,
        daily_avg_expense=daily_avg_expense,
        top_categories=top_categories,
        expense_count=len(expenses),
        income_count=len(incomes)
    )

@main.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'application': 'running'
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code
