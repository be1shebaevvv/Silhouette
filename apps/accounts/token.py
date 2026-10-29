from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomTokenGenerator(PasswordResetTokenGenerator):
    """Use Django's state-aware hash and invalidate a token after verification."""

    def _make_hash_value(self, user, timestamp):
        return super()._make_hash_value(user, timestamp) + str(user.is_verified)
