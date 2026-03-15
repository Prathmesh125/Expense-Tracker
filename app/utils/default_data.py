from app.models import Category, db

def create_default_categories(user_id):
    """
    Create default expense categories for a new user
    """
    default_categories = [
        {'name': 'Housing', 'description': 'Rent, mortgage, property taxes, utilities, repairs'},
        {'name': 'Transportation', 'description': 'Car payments, gas, public transit, vehicle maintenance'},
        {'name': 'Food', 'description': 'Groceries, dining out, coffee shops'},
        {'name': 'Healthcare', 'description': 'Insurance, medications, doctor visits, fitness'},
        {'name': 'Personal', 'description': 'Clothing, haircuts, personal care items'},
        {'name': 'Entertainment', 'description': 'Movies, concerts, subscriptions, hobbies'},
        {'name': 'Education', 'description': 'Tuition, books, courses, school supplies'},
        {'name': 'Debt', 'description': 'Credit card payments, loans, student loans'},
        {'name': 'Savings', 'description': 'Emergency fund, retirement, investments'},
        {'name': 'Gifts & Donations', 'description': 'Charitable donations, gifts for others'},
        {'name': 'Travel', 'description': 'Flights, hotels, vacation expenses'},
        {'name': 'Miscellaneous', 'description': 'Other expenses that don\'t fit in other categories'}
    ]
    
    for category in default_categories:
        # Check if the category already exists for this user
        existing = Category.query.filter_by(
            user_id=user_id,
            name=category['name']
        ).first()
        
        # Only create if it doesn't exist
        if not existing:
            new_category = Category(
                name=category['name'],
                description=category['description'],
                user_id=user_id
            )
            db.session.add(new_category)
    
    # Commit all changes at once
    db.session.commit()
