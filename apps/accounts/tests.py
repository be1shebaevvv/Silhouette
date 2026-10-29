from django.test import TestCase
from django.urls import reverse

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
            User.objects.create_user(
                username="",
                password="Safe-test-password-42",
                email="person@example.com",
            )

    def test_create_superuser_sets_privileged_flags(self):
        user = User.objects.create_superuser(
            username="site_admin",
            password="Safe-test-password-42",
            email="admin@example.com",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_unverified_user_cannot_log_in(self):
        User.objects.create_user(
            username="waiting_user",
            password="Safe-test-password-42",
            email="waiting@example.com",
            is_verified=False,
        )

        response = self.client.post(
            reverse("login"),
            {"username": "waiting_user", "password": "Safe-test-password-42"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Подтвердите адрес электронной почты")

    def test_public_profile_does_not_expose_private_identity_fields(self):
        user = User.objects.create_user(
            username="pseudonymous",
            password="Safe-test-password-42",
            email="private@example.com",
            first_name="PrivateFirst",
            last_name="PrivateLast",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("profil"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "private@example.com")
        self.assertNotContains(response, "PrivateFirst")
        self.assertNotContains(response, "PrivateLast")
