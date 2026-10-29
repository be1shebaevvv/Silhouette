from django.core import mail
from django.test import TestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.token import CustomTokenGenerator


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


    def test_user_can_block_and_unblock_another_user(self):
        blocker = User.objects.create_user(
            username="blocker",
            password="Safe-test-password-42",
            email="blocker@example.com",
        )
        blocked = User.objects.create_user(
            username="blocked",
            password="Safe-test-password-42",
            email="blocked@example.com",
        )
        self.client.force_login(blocker)

        response = self.client.post(reverse("block_user", kwargs={"user_id": blocked.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(blocker.blocked_users.filter(pk=blocked.pk).exists())

        self.client.post(reverse("unblock_user", kwargs={"user_id": blocked.pk}))
        self.assertFalse(blocker.blocked_users.filter(pk=blocked.pk).exists())


    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_registration_requires_and_supports_email_verification(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_pseudonym",
                "email": "new-pseudonym@example.com",
                "password1": "Another-safe-password-84",
                "password2": "Another-safe-password-84",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="new_pseudonym")
        self.assertFalse(user.is_verified)
        self.assertEqual(len(mail.outbox), 1)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = CustomTokenGenerator().make_token(user)
        activation = self.client.get(
            reverse("account_activate", kwargs={"uidb64": uid, "token": token})
        )

        self.assertEqual(activation.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(self.client.session.get("_auth_user_id"))


    def test_account_deletion_requires_current_password(self):
        user = User.objects.create_user(
            username="delete_me",
            password="Safe-test-password-42",
            email="delete-me@example.com",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("delete_account"), {"password": "wrong-password"})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_account_can_be_deleted_with_current_password(self):
        user = User.objects.create_user(
            username="delete_me_for_real",
            password="Safe-test-password-42",
            email="delete-me-for-real@example.com",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("delete_account"),
            {"password": "Safe-test-password-42"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
