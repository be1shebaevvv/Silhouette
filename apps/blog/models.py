from django.db import models

from apps.accounts.models import User


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField(max_length=150)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField("Название", max_length=100)
    description = models.TextField("Описание")
    media = models.FileField("Медиа", upload_to="posts/", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField("Активный", default=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_posts", blank=True)
    chats = models.ManyToManyField(User, related_name="chats", blank=True)

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-created_at"]

    @property
    def is_video(self):
        if not self.media:
            return False
        return self.media.name.lower().endswith((".mp4", ".webm", ".mov", ".m4v"))

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comments")
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return self.text[:80]


class ReplayComment(models.Model):
    """Legacy reply model retained for compatibility with existing migrations."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replay_comment")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_replay_comments")
    parent = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ответ на комментарий"
        verbose_name_plural = "Ответы на комментарии"

    def __str__(self):
        return self.text[:80]

class Report(models.Model):
    class Reason(models.TextChoices):
        SPAM = "spam", "Спам"
        HARASSMENT = "harassment", "Травля или угрозы"
        PRIVACY = "privacy", "Раскрытие личных данных"
        HATE = "hate", "Ненависть или опасный контент"
        OTHER = "other", "Другое"

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает проверки"
        REVIEWED = "reviewed", "Проверено"
        ACTION_TAKEN = "action_taken", "Приняты меры"
        DISMISSED = "dismissed", "Отклонено"

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    reason = models.CharField("Причина", max_length=20, choices=Reason.choices)
    details = models.TextField("Подробности", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"
        ordering = ["status", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, comment__isnull=True)
                    | models.Q(post__isnull=True, comment__isnull=False)
                ),
                name="report_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["reporter", "post"],
                condition=models.Q(post__isnull=False),
                name="unique_reporter_post",
            ),
            models.UniqueConstraint(
                fields=["reporter", "comment"],
                condition=models.Q(comment__isnull=False),
                name="unique_reporter_comment",
            ),
        ]

    def __str__(self):
        target = f"post #{self.post_id}" if self.post_id else f"comment #{self.comment_id}"
        return f"Report #{self.pk}: {target} ({self.get_status_display()})"
