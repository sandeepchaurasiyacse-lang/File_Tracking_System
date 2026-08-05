# Troubleshooting guide

## Common issues
- Missing dependencies: activate the virtual environment and reinstall requirements.
- Database errors: confirm migrations are current and restart the app after schema updates.
- Access issues: verify login and user mappings before testing file workflows.

## Diagnostic steps
1. Run python manage.py check
2. Inspect the Django logs
3. Confirm environment values are set correctly
4. Re-run the previous feature test sequence
