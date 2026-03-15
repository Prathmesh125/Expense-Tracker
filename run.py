import os
from app import create_app
from flask_migrate import Migrate
from app.models import db, User, Expense, Category, Income
import click
from flask.cli import with_appcontext
from app.utils.default_data import create_default_categories

app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)

# Set the application to run on port 5003 by default but allow overriding via command line
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5003, help='Port to run the application on')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Expense=Expense, Category=Category, Income=Income)

@app.cli.command('add-default-categories')
@click.argument('user_id', type=int, required=False)
@with_appcontext
def add_default_categories(user_id=None):
    """Add default categories to users
    
    If user_id is provided, add categories only to that user.
    If no user_id is provided, add categories to all users.
    """
    if user_id:
        user = User.query.get(user_id)
        if not user:
            click.echo(f"Error: No user found with ID {user_id}")
            return
        create_default_categories(user.id)
        click.echo(f"Default categories added for user {user.username} (ID: {user.id})")
    else:
        users = User.query.all()
        for user in users:
            create_default_categories(user.id)
        click.echo(f"Default categories added for {len(users)} users")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
