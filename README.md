# Silhouette

Silhouette is an anonymous-first social platform built with Django. Its goal is to let people publish thoughts, discuss posts, discover communities, and message one another without requiring a public real-name identity.

## Current stack

- Python and Django
- SQLite for local development
- Django templates and static CSS
- Email verification, password recovery, and password-confirmed account deletion
- Pseudonymous profiles, user blocking, content reports, and moderator tools
- Text-first posts, threaded comments, reactions, follows, and private messaging
- Django REST Framework (API groundwork)

## Local setup

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and replace the sample secret with a generated key:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Put the generated value in `DJANGO_SECRET_KEY` in `.env`. The `.env` file is ignored by Git. Never reuse the example value in a deployed environment.

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

Silhouette is designed for pseudonymous participation: public profiles show a nickname, not the account email or real name. Users can block other accounts and report posts or comments; reports are available to moderators in Django admin. This is not absolute anonymity: hosting providers may process technical metadata, and users can reveal themselves through their own content or media. Deployment should use HTTPS, limit collection and retention of technical data, protect account information, and clearly explain what administrators and infrastructure providers can access.

## Tests and checks

Run the Django test suite with:

```bash
python manage.py test
python manage.py check
```

This README describes the current development setup. Deployment should not be considered production-ready until the full security review, operational configuration, backups, rate limiting, and deployment-specific checks are complete.
