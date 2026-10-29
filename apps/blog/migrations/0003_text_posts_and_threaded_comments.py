from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0002_remove_replaycomment_parent_comment_post_chats_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ["name"], "verbose_name": "Категория", "verbose_name_plural": "Категории"},
        ),
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ["-created_at"], "verbose_name": "Публикация", "verbose_name_plural": "Публикации"},
        ),
        migrations.AlterModelOptions(
            name="comment",
            options={"ordering": ["created_at"], "verbose_name": "Комментарий", "verbose_name_plural": "Комментарии"},
        ),
        migrations.AlterModelOptions(
            name="replaycomment",
            options={"verbose_name": "Ответ на комментарий", "verbose_name_plural": "Ответы на комментарии"},
        ),
        migrations.AlterField(
            model_name="post",
            name="media",
            field=models.FileField(blank=True, null=True, upload_to="posts/", verbose_name="Медиа"),
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to="blog.category"),
        ),
        migrations.AlterField(
            model_name="post",
            name="likes",
            field=models.ManyToManyField(blank=True, related_name="liked_posts", to="accounts.user"),
        ),
        migrations.AlterField(
            model_name="post",
            name="dislikes",
            field=models.ManyToManyField(blank=True, related_name="disliked_posts", to="accounts.user"),
        ),
        migrations.AlterField(
            model_name="post",
            name="chats",
            field=models.ManyToManyField(blank=True, related_name="chats", to="accounts.user"),
        ),
        migrations.AlterField(
            model_name="comment",
            name="parent_comment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name="replies",
                to="blog.comment",
            ),
        ),
    ]
