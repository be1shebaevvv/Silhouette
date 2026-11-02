from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.message.models import Message


class PrivateChatTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            username="alice",
            password="Safe-test-password-42",
            email="alice@example.com",
        )
        self.bob = User.objects.create_user(
            username="bob",
            password="Safe-test-password-42",
            email="bob@example.com",
        )
        self.eve = User.objects.create_user(
            username="eve",
            password="Safe-test-password-42",
            email="eve@example.com",
        )
        self.secret_message = Message.objects.create(
            sender=self.alice,
            recipient=self.bob,
            content="This is private between Alice and Bob.",
        )

    def test_chat_list_requires_authentication(self):
        response = self.client.get(reverse("list_chat"))
        self.assertEqual(response.status_code, 302)

    def test_third_party_cannot_read_another_conversation(self):
        self.client.force_login(self.eve)

        response = self.client.get(reverse("chats", kwargs={"recipient_id": self.bob.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This is private between Alice and Bob.")

    def test_message_search_does_not_show_current_user_as_recipient(self):
        self.client.force_login(self.alice)

        response = self.client.get(reverse("searchs"), {"query": "bob"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "@bob")
        self.assertNotContains(response, "@alice")


    def test_blocked_users_cannot_open_private_chat(self):
        self.client.force_login(self.alice)
        self.alice.blocked_users.add(self.bob)

        response = self.client.get(reverse("chats", kwargs={"recipient_id": self.bob.pk}))

        self.assertEqual(response.status_code, 403)


class MessageValidationTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="message_sender",
            password="Safe-test-password-42",
            email="message-sender@example.com",
        )
        self.recipient = User.objects.create_user(
            username="message_recipient",
            password="Safe-test-password-42",
            email="message-recipient@example.com",
        )
        self.client.force_login(self.sender)

    def test_empty_message_is_not_saved(self):
        response = self.client.post(
            reverse("chats", kwargs={"recipient_id": self.recipient.pk}),
            {"content": "   "},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 0)

    def test_message_content_is_limited_to_5000_characters(self):
        response = self.client.post(
            reverse("chats", kwargs={"recipient_id": self.recipient.pk}),
            {"content": "x" * 6000},
        )

        self.assertEqual(response.status_code, 302)
        message = Message.objects.get(sender=self.sender, recipient=self.recipient)
        self.assertEqual(len(message.content), 5000)
