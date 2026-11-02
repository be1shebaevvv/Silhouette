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
| `DATABASE_URL` | Optional database URL; use PostgreSQL for deployment |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP server settings |
| `EMAIL_USER`, `EMAIL_PASSWORD` | SMTP credentials; never commit these |
| `DEFAULT_FROM_EMAIL` | Sender address |

Without SMTP credentials, emails are printed to the development console instead of being sent.

## Share on a trusted local Wi-Fi network

For temporary testing with devices connected to the same trusted Wi-Fi network:

1. Find the host computer's IPv4 address with `ipconfig` on Windows.
2. Add that address to `DJANGO_ALLOWED_HOSTS` in the local, untracked `.env` file. For example: `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,10.0.0.25`. Use the actual address assigned by your router; it may change.
3. Start Django bound to the local network interface:

   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```

4. From another device on the same Wi-Fi, open `http://HOST_IPV4:8000/`, replacing `HOST_IPV4` with the host computer's address.
5. If Windows Firewall prompts you, allow Python only on **Private** networks. Do not expose the development server to public networks or the internet.

The laptop must remain powered on and the development server must keep running. This is for trusted-LAN testing only: Django's development server is not production-grade, HTTP traffic is not encrypted, and users on the same network may be able to observe traffic. Do not use real passwords or sensitive personal information in this setup. For broader access, deploy behind HTTPS with a production WSGI/ASGI server.

## Privacy and anonymity

Silhouette is designed for pseudonymous participation: public profiles show a nickname, not the account email or real name. Users can block other accounts and report posts or comments; reports are available to moderators in Django admin. This is not absolute anonymity: hosting providers may process technical metadata, and users can reveal themselves through their own content or media. Deployment should use HTTPS, limit collection and retention of technical data, protect account information, and clearly explain what administrators and infrastructure providers can access.

## Production deployment checklist

Before exposing the site publicly:

1. Set `DJANGO_DEBUG=False` and generate a strong, unique `DJANGO_SECRET_KEY`.
2. Set `DJANGO_ALLOWED_HOSTS` to the exact domain names and `DJANGO_CSRF_TRUSTED_ORIGINS` to HTTPS origins.
3. Configure `DATABASE_URL` for PostgreSQL. SQLite is intended for local development, not a multi-user production deployment.
4. Configure real SMTP credentials in `EMAIL_USER` and `EMAIL_PASSWORD`; the console email backend is only for development.
5. Run migrations and collect static assets:

   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py check --deploy
   ```

6. Use HTTPS, persistent/private media storage, backups, monitoring, and an appropriate reverse-proxy configuration. Review data retention and privacy disclosures before launch.

## Tests and checks

Run the Django test suite with:

```bash
python manage.py test
python manage.py check
```

This README describes the current development setup. Deployment should not be considered production-ready until the full security review, operational configuration, backups, rate limiting, and deployment-specific checks are complete.
