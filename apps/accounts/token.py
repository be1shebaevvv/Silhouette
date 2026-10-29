from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomTokenGenerator(PasswordResetTokenGenerator):
    """Use Django's built-in, state-aware token hashing.

    The inherited implementation invalidates tokens when security-sensitive
    account state changes and applies Django's standard token timeout.
    """

    pass
