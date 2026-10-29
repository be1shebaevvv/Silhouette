from django.conf import settings
from django.db import migrations, models
import apps.accounts.models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_gender"),
    ]

    operations = [
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
