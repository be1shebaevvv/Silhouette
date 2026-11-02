from django.conf import settings
from django.db import migrations, models
import apps.accounts.models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="users/profiles_images/", verbose_name="Аватарка"),
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", apps.accounts.models.UserManager()),
            ],
        ),
    ]
