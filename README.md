# File Tracking System

This Django project manages employee records, department metadata, authentication, and file-upload history for internal operations.

## Project focus
- Maintain secure login and user access across the application.
- Organize employees and departments into an admin-friendly structure.
- Track uploaded files and their history across workflows.
- Support file-related auditing for operational review.

## Key modules
- `fms/` contains core Django project settings and routing.
- `myapp/` contains application models, views, and supporting logic.
- `manage.py` starts the local Django development server.

## Status
The project is under active development and is being prepared for feature completion and operational review.
## Local setup

See [docs/setup.md](docs/setup.md) for the development environment steps and validation commands.
## Environment configuration

The project should be configured with a local environment file before running in a development or staging context. See [docs/environment.md](docs/environment.md).
## File tracking workflow

The operational flow for uploaded records is described in [docs/file-workflow.md](docs/file-workflow.md).
## Employee and department structure

Core model relationships are outlined in [docs/employee-department.md](docs/employee-department.md).
