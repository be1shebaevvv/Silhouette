from django.test import TestCase

from apps.accounts.models import User


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self):
        user = User.objects.create_user(
            username="quiet_user",
            password="Safe-test-password-42",
            email="Person@EXAMPLE.COM",
        )

        self.assertEqual(user.email, "Person@example.com")
        self.assertTrue(user.check_password("Safe-test-password-42"))
        self.assertNotEqual(user.password, "Safe-test-password-42")

    def test_create_user_requires_username(self):
        with self.assertRaisesMessage(ValueError, "A username must be provided."):
            User.objects.create_user(username="", password="Safe-test-password-42", email="person@example.com")

    def test_create_superuser_sets_privileged_flags(self):
        user = User.objects.create_superuser(
            username="site_admin",
            password="Safe-test-password-42",
            email="admin@example.com",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
