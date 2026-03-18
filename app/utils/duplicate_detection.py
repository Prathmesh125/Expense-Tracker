"""
Duplicate detection utilities for expenses and incomes
"""
from app.models import Expense, Income
from datetime import timedelta

def find_similar_expenses(user_id, amount, date, description, expense_id=None, threshold_days=3):
    """
    Find similar expenses that might be duplicates
    
    Args:
        user_id: User ID to search within
        amount: Expense amount
        date: Expense date
        description: Expense description
        expense_id: ID of current expense (to exclude from results when updating)
        threshold_days: Number of days to look before/after for potential duplicates
    
    Returns:
        List of potentially duplicate expenses
    """
    # Calculate date range
    start_date = date - timedelta(days=threshold_days)
    end_date = date + timedelta(days=threshold_days)
    
    # Query for similar expenses
    query = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.amount == amount,
        Expense.date >= start_date,
        Expense.date <= end_date
    )
    
    # Exclude current expense if updating
    if expense_id:
        query = query.filter(Expense.id != expense_id)
    
    similar = query.all()
    
    # Further filter by description similarity if description exists
    if description and similar:
        filtered = []
        desc_lower = description.lower() if description else ""
        for exp in similar:
            exp_desc_lower = exp.description.lower() if exp.description else ""
            # Simple similarity check: same words or substring match
            if desc_lower in exp_desc_lower or exp_desc_lower in desc_lower:
                filtered.append(exp)
        return filtered
    
    return similar

def find_similar_incomes(user_id, amount, date, source, income_id=None, threshold_days=3):
    """
    Find similar incomes that might be duplicates
    
    Args:
        user_id: User ID to search within
        amount: Income amount
        date: Income date
        source: Income source
        income_id: ID of current income (to exclude from results when updating)
        threshold_days: Number of days to look before/after for potential duplicates
    
    Returns:
        List of potentially duplicate incomes
    """
    # Calculate date range
    start_date = date - timedelta(days=threshold_days)
    end_date = date + timedelta(days=threshold_days)
    
    # Query for similar incomes
    query = Income.query.filter(
        Income.user_id == user_id,
        Income.amount == amount,
        Income.date >= start_date,
        Income.date <= end_date
    )
    
    # Exclude current income if updating
    if income_id:
        query = query.filter(Income.id != income_id)
    
    similar = query.all()
    
    # Further filter by source similarity if source exists
    if source and similar:
        filtered = []
        source_lower = source.lower() if source else ""
        for inc in similar:
            inc_source_lower = inc.source.lower() if inc.source else ""
            if source_lower == inc_source_lower:
                filtered.append(inc)
        return filtered
    
    return similar

def check_duplicate_risk(similar_items, threshold=1):
    """
    Check if the number of similar items indicates duplicate risk
    
    Args:
        similar_items: List of similar expenses/incomes
        threshold: Minimum number of similar items to constitute a risk
    
    Returns:
        Tuple of (is_duplicate_risk, warning_message)
    """
    count = len(similar_items)
    
    if count == 0:
        return False, None
    elif count == 1:
        return True, f"Found 1 similar transaction on {similar_items[0].date.strftime('%Y-%m-%d')}. Please verify this is not a duplicate."
    else:
        return True, f"Found {count} similar transactions. Please verify these are not duplicates."
