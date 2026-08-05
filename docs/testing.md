# Testing and validation

The project should be validated after schema or workflow changes.

## Recommended checks
- python manage.py check
- python manage.py test
- Review migration output after updating models

## Regression mindset
Whenever a file tracking or login change is introduced, run the full validation path before opening the branch for review.
