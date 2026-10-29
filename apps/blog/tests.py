from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.blog.forms import PostCreationForm
from apps.blog.models import Comment, Post, Report


class PostAndDiscussionTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="post_author",
            password="Safe-test-password-42",
            email="author@example.com",
        )
        self.post = Post.objects.create(
            title="A text-only post",
            description="This should work without an uploaded file.",
            author=self.author,
        )

    def test_text_only_post_can_be_opened(self):
        response = self.client.get(reverse("post_detail", kwargs={"pk": self.post.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A text-only post")
        self.assertContains(response, "This should work without an uploaded file.")

    def test_homepage_renders_popular_and_recent_posts(self):
        response = self.client.get(reverse("list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A text-only post")
        self.assertContains(response, "Приватность — в основе")

    def test_only_author_can_edit_post(self):
        other_user = User.objects.create_user(
            username="other_user",
            password="Safe-test-password-42",
            email="other@example.com",
        )
        self.client.force_login(other_user)

        response = self.client.get(reverse("post-edit", kwargs={"pk": self.post.pk}))

        self.assertEqual(response.status_code, 403)

    def test_comment_reply_is_linked_to_parent(self):
        parent = Comment.objects.create(
            author=self.author,
            post=self.post,
            text="Original comment",
        )
        replier = User.objects.create_user(
            username="reply_author",
            password="Safe-test-password-42",
            email="reply@example.com",
        )
        self.client.force_login(replier)

        response = self.client.post(
            reverse("reply_to_comment", kwargs={"comment_id": parent.pk}),
            {"text": "A real threaded reply"},
        )

        self.assertEqual(response.status_code, 302)
        reply = Comment.objects.get(text="A real threaded reply")
        self.assertEqual(reply.parent_comment, parent)
        self.assertEqual(reply.post, self.post)

    def test_like_action_toggles_reaction(self):
        self.client.force_login(self.author)
        url = reverse("like_dislike_post", kwargs={"post_id": self.post.pk})

        response = self.client.post(url, {"action": "like"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.post.likes.filter(pk=self.author.pk).exists())

        self.client.post(url, {"action": "like"})
        self.assertFalse(self.post.likes.filter(pk=self.author.pk).exists())

    def test_post_form_accepts_text_only_publication(self):
        form = PostCreationForm(data={
            "title": "Only text",
            "description": "No file is required.",
            "category": "",
            "is_active": "on",
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_post_form_rejects_unapproved_file_extensions(self):
        upload = SimpleUploadedFile("payload.html", b"<script>alert(1)</script>")
        form = PostCreationForm(
            data={"title": "Unsafe attachment", "description": "A file", "category": "", "is_active": "on"},
            files={"media": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("media", form.errors)


class ContentReportingTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="content_author",
            password="Safe-test-password-42",
            email="content-author@example.com",
        )
        self.reporter = User.objects.create_user(
            username="reporter",
            password="Safe-test-password-42",
            email="reporter@example.com",
        )
        self.post = Post.objects.create(
            title="Reported post",
            description="Example content",
            author=self.author,
        )

    def test_user_can_report_a_post_once(self):
        self.client.force_login(self.reporter)
        url = reverse("report_post", kwargs={"post_id": self.post.pk})

        response = self.client.post(url, {"reason": "spam", "details": "Repeated advertisements"})

        self.assertEqual(response.status_code, 302)
        report = Report.objects.get(reporter=self.reporter, post=self.post)
        self.assertEqual(report.status, Report.Status.PENDING)

        self.client.post(url, {"reason": "other", "details": "Duplicate"})
        self.assertEqual(Report.objects.filter(reporter=self.reporter, post=self.post).count(), 1)

    def test_author_cannot_report_own_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("report_post", kwargs={"post_id": self.post.pk}),
            {"reason": "other", "details": ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Report.objects.filter(reporter=self.author, post=self.post).exists())


    def test_only_author_can_delete_post(self):
        other_user = User.objects.create_user(
            username="delete_other",
            password="Safe-test-password-42",
            email="delete-other@example.com",
        )
        self.client.force_login(other_user)

        response = self.client.post(reverse("delete_post", kwargs={"post_id": self.post.pk}))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_author_can_delete_own_post(self):
        self.client.force_login(self.author)

        response = self.client.post(reverse("delete_post", kwargs={"post_id": self.post.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
