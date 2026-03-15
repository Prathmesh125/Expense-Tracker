#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Add default categories for new users (optional)
# flask add-default-categories
