# Silhouette

Silhouette is an anonymous-first social platform built with Django. Its goal is to let people publish thoughts, discuss posts, discover communities, and message one another without requiring a public real-name identity.

## Current stack

- Python and Django
- SQLite for local development
- Django templates and static CSS
- Django REST Framework (API groundwork)

## Local setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Set a local secret key (recommended even for development):

   **Windows PowerShell**
   ```powershell
   $env:DJANGO_SECRET_KEY = "replace-with-a-random-local-secret"
   ```

   **macOS/Linux**
   ```bash
   export DJANGO_SECRET_KEY="replace-with-a-random-local-secret"
   ```

5. Apply migrations and create an administrator:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

6. Open http://127.0.0.1:8000/

## Configuration

Settings are read from environment variables. Common options:

| Variable | Purpose |
| --- | --- |
| `DJANGO_DEBUG` | Enable debug mode; defaults to true for local development |
| `DJANGO_SECRET_KEY` | Django secret key; required when debug mode is disabled |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed host names |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins, including scheme |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP server settings |
| `EMAIL_USER`, `EMAIL_PASSWORD` | SMTP credentials; never commit these |
| `DEFAULT_FROM_EMAIL` | Sender address |

Without SMTP credentials, emails are printed to the development console instead of being sent.

## Privacy and anonymity

Silhouette is intended to support pseudonymous participation, not to promise absolute anonymity. Deployment should use HTTPS, limit collection and retention of technical data, protect account information, and clearly explain what administrators and infrastructure providers can access.

## Tests and checks

Run the Django test suite with:

```bash
python manage.py test
python manage.py check
```

This README describes the current development setup. Deployment should not be considered production-ready until the security review, tests, media handling, moderation, and operational configuration are complete.
