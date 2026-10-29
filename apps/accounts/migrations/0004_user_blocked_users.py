from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_verification_and_manager"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="blocked_users",
            field=models.ManyToManyField(blank=True, related_name="blocked_by", to="accounts.user"),
        ),
    ]
