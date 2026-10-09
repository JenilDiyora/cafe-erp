#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install production dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files into staticfiles directory
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Seed initial cafe settings, opening hours, menu categories, tables, and demo data
python manage.py seed_cafe_data
python manage.py seed_phase2_data

