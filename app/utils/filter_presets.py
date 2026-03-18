"""
Filter presets for quick expense filtering
"""
from datetime import datetime, timedelta

def get_filter_presets():
    """Get predefined filter presets for quick access"""
    today = datetime.today()
    
    presets = {
        'today': {
            'name': 'Today',
            'icon': 'fa-calendar-day',
            'date_filter': 'custom',
            'start_date': today.strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d')
        },
        'yesterday': {
            'name': 'Yesterday',
            'icon': 'fa-calendar-minus',
            'date_filter': 'custom',
            'start_date': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (today - timedelta(days=1)).strftime('%Y-%m-%d')
        },
        'this_week': {
            'name': 'This Week',
            'icon': 'fa-calendar-week',
            'date_filter': 'custom',
            'start_date': (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d')
        },
        'last_7_days': {
            'name': 'Last 7 Days',
            'icon': 'fa-calendar',
            'date_filter': 'custom',
            'start_date': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d')
        },
        'last_30_days': {
            'name': 'Last 30 Days',
            'icon': 'fa-calendar-alt',
            'date_filter': 'custom',
            'start_date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d')
        },
        'this_month': {
            'name': 'This Month',
            'icon': 'fa-calendar-check',
            'date_filter': 'this_month'
        },
        'last_month': {
            'name': 'Last Month',
            'icon': 'fa-calendar-times',
            'date_filter': 'last_month'
        },
        'this_quarter': {
            'name': 'This Quarter',
            'icon': 'fa-calendar-plus',
            'date_filter': 'custom',
            'start_date': get_quarter_start(today).strftime('%Y-%m-%d'),
            'end_date': today.strftime('%Y-%m-%d')
        },
        'this_year': {
            'name': 'This Year',
            'icon': 'fa-calendar',
            'date_filter': 'this_year'
        }
    }
    
    return presets

def get_quarter_start(date):
    """Get the start date of the current quarter"""
    quarter = (date.month - 1) // 3
    month = quarter * 3 + 1
    return datetime(date.year, month, 1)

def get_amount_range_presets():
    """Get predefined amount range presets"""
    return {
        'small': {'name': 'Small (< ₹500)', 'max': 500},
        'medium': {'name': 'Medium (₹500 - ₹2000)', 'min': 500, 'max': 2000},
        'large': {'name': 'Large (₹2000 - ₹10000)', 'min': 2000, 'max': 10000},
        'very_large': {'name': 'Very Large (> ₹10000)', 'min': 10000}
    }
