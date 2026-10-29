# Environment reference

Use a local environment file for deployment-specific configuration.

## Suggested values
- `DEBUG=True` for development
- `SECRET_KEY=<your-secret-value>`
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- `DATABASE_URL=sqlite:///db.sqlite3`

## Notes
Keep the file out of source control and use placeholder values in shared documentation.
