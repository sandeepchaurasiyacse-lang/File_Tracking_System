# Local setup guide

Follow these steps to run the project on a local machine.

## Requirements
- Python 3.11+
- Django-compatible virtual environment
- SQLite for local development

## Installation
1. Create a virtual environment:
   python -m venv .venv
2. Activate it:
   .\.venv\Scripts\Activate.ps1
3. Install dependencies:
   python -m pip install --upgrade pip
   python -m pip install django
4. Apply migrations:
   python manage.py migrate
5. Start the app:
   python manage.py runserver

## Useful checks
- python manage.py check
- python manage.py test
