from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Expense, Income, Category, Budget
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
    
    # Calculate totals
    total_expense = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)
    balance = total_income - total_expense
    
    # Get expense by category data for pie chart
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
    
    return render_template(
        'main/dashboard.html',
        title='Dashboard',
        today=today,  # Add today variable
        total_expense=total_expense,
        total_income=total_income,
        balance=balance,
        category_chart=category_chart,
        income_expense_chart=income_expense_chart,
        last_expenses=last_expenses,
        last_incomes=last_incomes
    )
