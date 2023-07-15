# Generated by Django 4.2.2 on 2023-07-06 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('Мужской', 'Мужской'), ('Женский', 'Женский'), ('Неизвестный', 'Неизвестный')], default='Неизвестный', max_length=20, verbose_name='Пол'),
        ),
    ]
