from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.token import CustomTokenGenerator


token_generator = CustomTokenGenerator()


def send_activation_email(user, request, to_email):
    context = {
        "domain": get_current_site(request),
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": token_generator.make_token(user),
        "user": user,
    }
    message = render_to_string("register_confirm_email.html", context)
    email = EmailMessage(
        subject="Подтверждение аккаунта Silhouette",
        body=message,
        to=[to_email],
    )
    email.content_subtype = "html"
    return email.send(fail_silently=False)
