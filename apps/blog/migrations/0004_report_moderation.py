import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_verification_and_manager"),
        ("blog", "0003_text_posts_and_threaded_comments"),
    ]

    operations = [
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.CharField(choices=[("spam", "Спам"), ("harassment", "Травля или угрозы"), ("privacy", "Раскрытие личных данных"), ("hate", "Ненависть или опасный контент"), ("other", "Другое")], max_length=20, verbose_name="Причина")),
                ("details", models.TextField(blank=True, verbose_name="Подробности")),
                ("status", models.CharField(choices=[("pending", "Ожидает проверки"), ("reviewed", "Проверено"), ("action_taken", "Приняты меры"), ("dismissed", "Отклонено")], default="pending", max_length=20, verbose_name="Статус")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("comment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="blog.comment")),
                ("post", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="blog.post")),
                ("reporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports_made", to="accounts.user")),
            ],
            options={
                "verbose_name": "Жалоба",
                "verbose_name_plural": "Жалобы",
                "ordering": ["status", "-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="report",
            constraint=models.CheckConstraint(
                condition=models.Q(models.Q(("comment__isnull", True), ("post__isnull", False)), models.Q(("comment__isnull", False), ("post__isnull", True)), _connector="OR"),
                name="report_exactly_one_target",
            ),
        ),
        migrations.AddConstraint(
            model_name="report",
            constraint=models.UniqueConstraint(condition=models.Q(("post__isnull", False)), fields=("reporter", "post"), name="unique_reporter_post"),
        ),
        migrations.AddConstraint(
            model_name="report",
            constraint=models.UniqueConstraint(condition=models.Q(("comment__isnull", False)), fields=("reporter", "comment"), name="unique_reporter_comment"),
        ),
    ]
